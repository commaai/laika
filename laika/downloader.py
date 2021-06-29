import certifi # type: ignore
import ftplib
import hatanaka
import os
import urllib.request
import pycurl # type: ignore
import time
import tempfile

from datetime import datetime
from urllib.parse import urlparse
from io import BytesIO

from .constants import SECS_IN_HR, SECS_IN_DAY, SECS_IN_WEEK
from .gps_time import GPSTime

dir_path = os.path.dirname(os.path.realpath(__file__))


def retryable(f):
  """
  Decorator to allow us to pass multiple URLs from which to download.
  Automatically retry the request with the next URL on failure
  """
  def wrapped(url_bases, *args, **kwargs):
    if isinstance(url_bases, str):
      # only one url passed, don't do the retry thing
      return f(url_bases, *args, **kwargs)

    # not a string, must be a list of url_bases
    for url_base in url_bases:
      try:
        return f(url_base, *args, **kwargs)
      except IOError as e:
        print(e)
    # none of them succeeded
    raise IOError("Multiple URL failures attempting to pull file(s)")
  return wrapped

def ftp_connect(url):
  parsed = urlparse(url)
  assert parsed.scheme == 'ftp'
  try:
    domain = parsed.netloc
    ftp = ftplib.FTP(domain)
    ftp.login()
  except (OSError, ftplib.error_perm):
    raise IOError("Could not connect/auth to: " + domain)
  try:
    ftp.cwd(parsed.path)
  except ftplib.error_perm:
    raise IOError("Permission failure with folder: " + url)
  return ftp

@retryable
def list_dir(url):
  try:
    ftp = ftp_connect(url)
    return ftp.nlst()
  except ftplib.error_perm:
    raise IOError("Permission failure listing folder: " + url)

def ftp_download_files(url_base, folder_path, cacheDir, filenames, compression='', overwrite=False):
  """
  Like download file, but more of them. Keeps a persistent FTP connection open
  to be more efficient.
  """
  folder_path_abs = os.path.join(cacheDir, folder_path)

  ftp = ftp_connect(url_base + folder_path)

  filepaths = []
  for filename in filenames:
    filename_zipped = filename + compression
    filepath = str(hatanaka.get_decompressed_path(os.path.join(folder_path_abs, filename)))
    filepath_zipped = os.path.join(folder_path_abs, filename_zipped)
    print("pulling from", url_base, "to", filepath)

    if not os.path.isfile(filepath) or overwrite:
      if not os.path.exists(folder_path_abs):
        os.makedirs(folder_path_abs)
      try:
        ftp.retrbinary('RETR ' + filename_zipped, open(filepath_zipped, 'wb').write)
      except (ftplib.error_perm):
        raise IOError("Could not download file from: " + url_base + folder_path + filename_zipped)
      filepaths.append(str(hatanaka.decompress_on_disk(filepath_zipped)))
    else:
      filepaths.append(filepath)
  return filepaths


def https_download_file(url):

  if os.path.isfile(dir_path + '/.netrc'):
    netrc_path = dir_path + '/.netrc'
    f = None
  else:
    try:
      username = os.environ['NASA_USERNAME']
      password = os.environ['NASA_PASSWORD']
      f = tempfile.NamedTemporaryFile()
      netrc = f"machine urs.earthdata.nasa.gov login {username} password {password}"
      f.write(netrc.encode())
      f.flush()
      netrc_path = f.name
    except KeyError:
      raise IOError('Could not find .netrc file and no NASA_USERNAME and NASA_PASSWORD in enviroment for urs.earthdata.nasa.gov authentication')

  crl = pycurl.Curl()
  crl.setopt(crl.CAINFO, certifi.where())
  crl.setopt(crl.URL, url)
  crl.setopt(crl.FOLLOWLOCATION, True)
  crl.setopt(crl.NETRC_FILE, netrc_path)
  crl.setopt(crl.NETRC, 2)
  crl.setopt(crl.SSL_CIPHER_LIST, 'DEFAULT@SECLEVEL=1')
  crl.setopt(crl.COOKIEJAR, '/tmp/cddis_cookies')
  crl.setopt(pycurl.CONNECTTIMEOUT, 10)

  buf = BytesIO()
  crl.setopt(crl.WRITEDATA, buf)
  crl.perform()
  response = crl.getinfo(pycurl.RESPONSE_CODE)
  crl.close()
  if f is not None:
    f.close()

  if response != 200:
    raise IOError('HTTPS error ' + str(response))
  return buf.getvalue()


def ftp_download_file(url):
  urlf = urllib.request.urlopen(url)
  data_zipped = urlf.read()
  urlf.close()
  return data_zipped


@retryable
def download_files(url_base, folder_path, cacheDir, filenames, compression='', overwrite=False):
  return ftp_download_files(
    url_base, folder_path, cacheDir, filenames, compression=compression, overwrite=overwrite
  )


@retryable
def download_file(url_base, folder_path, filename_zipped):
  url = url_base + folder_path + filename_zipped
  print('Downloading ' + url)
  if 'https' in url:
    data_zipped = https_download_file(url)
  elif 'ftp':
    data_zipped = ftp_download_file(url)
  else:
    raise NotImplementedError('Did find ftp or https preamble')
  return data_zipped


def download_and_cache_file(url_base, folder_path, cacheDir, filename, compression='', overwrite=False):
  folder_path_abs = os.path.join(cacheDir, folder_path)
  filename_zipped = filename + compression

  filepath = str(hatanaka.get_decompressed_path(os.path.join(folder_path_abs, filename)))
  filepath_attempt = filepath + '.attempt_time'
  filepath_zipped = os.path.join(folder_path_abs, filename_zipped)

  if os.path.exists(filepath_attempt):
    with open(filepath_attempt, 'rb') as rf:
      last_attempt_time = float(rf.read().decode())
    if time.time() - last_attempt_time < SECS_IN_HR:
      raise IOError(f"Too soon to try  {folder_path + filename_zipped} from {url_base} ")

  if not os.path.isfile(filepath) or overwrite:
    if not os.path.exists(folder_path_abs):
      os.makedirs(folder_path_abs)

    try:
      data_zipped = download_file(url_base, folder_path, filename_zipped)
    except (IOError, pycurl.error):
      unix_time = time.time()
      if not os.path.exists(cacheDir + 'tmp/'):
        os.makedirs(cacheDir + '/tmp')
      with tempfile.NamedTemporaryFile(delete=False, dir=cacheDir+'tmp/') as fout:
        fout.write(str.encode(str(unix_time)))
      os.replace(fout.name, filepath + '.attempt_time')
      raise IOError(f"Could not download {folder_path + filename_zipped} from {url_base} ")


    with open(filepath_zipped, 'wb') as wf:
      wf.write(data_zipped)

    filepath = str(hatanaka.decompress_on_disk(filepath_zipped))
  return filepath


def download_nav(time, cache_dir, constellation='GPS'):
  t = time.as_datetime()
  try:
    if GPSTime.from_datetime(datetime.utcnow()) - time > SECS_IN_DAY:
      url_bases = (
        'https://github.com/commaai/gnss-data/raw/master/gnss/data/daily/',
        'https://cddis.nasa.gov/archive/gnss/data/daily/',
      )
      cache_subdir = cache_dir + 'daily_nav/'
      if constellation =='GPS':
        filename = t.strftime("brdc%j0.%yn")
        folder_path = t.strftime('%Y/%j/%yn/')
      elif constellation =='GLONASS':
        filename = t.strftime("brdc%j0.%yg")
        folder_path = t.strftime('%Y/%j/%yg/')
      compression = '.gz' if folder_path >= '2020/335/' else '.Z'
      return download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression=compression)
    else:
      url_base = 'https://cddis.nasa.gov/archive/gnss/data/hourly/'
      cache_subdir = cache_dir + 'hourly_nav/'
      if constellation =='GPS':
        filename = t.strftime("hour%j0.%yn")
        folder_path = t.strftime('%Y/%j/')
        compression = '.gz' if folder_path >= '2020/336/' else '.Z'
        return download_and_cache_file(url_base, folder_path, cache_subdir, filename, compression=compression, overwrite=True)
  except IOError:
    pass


def download_orbits(time, cache_dir):
  cache_subdir = cache_dir + 'cddis_products/'
  url_bases = (
    'https://github.com/commaai/gnss-data/raw/master/gnss/products/',
    'https://cddis.nasa.gov/archive/gnss/products/',
    'ftp://igs.ign.fr/pub/igs/products/',
  )
  downloaded_files = []
  for time in [time - SECS_IN_DAY, time, time + SECS_IN_DAY]:
    folder_path = "%i/" % (time.week)
    if GPSTime.from_datetime(datetime.utcnow()) - time > 3*SECS_IN_WEEK:
      try:
        filename = "igs%i%i.sp3" % (time.week, time.day)
        downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.Z'))
        continue
      except IOError:
        pass
    try:
      filename = "igr%i%i.sp3" % (time.week, time.day)
      downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.Z'))
      continue
    except IOError:
      pass
    try:
      filename = "igu%i%i_18.sp3" % (time.week, time.day)
      downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.Z'))
      continue
    except IOError:
      pass
    try:
      filename = "igu%i%i_12.sp3" % (time.week, time.day)
      downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.Z'))
      continue
    except IOError:
      pass
    try:
      filename = "igu%i%i_06.sp3" % (time.week, time.day)
      downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.Z'))
      continue
    except IOError:
      pass
    try:
      filename = "igu%i%i_00.sp3" % (time.week, time.day)
      downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.Z'))
      continue
    except IOError:
      pass
  return downloaded_files


def download_orbits_russia(time, cache_dir):
  cache_subdir = cache_dir + 'russian_products/'
  url_bases = (
    'https://github.com/commaai/gnss-data-alt/raw/master/MCC/PRODUCTS/',
    'ftp://ftp.glonass-iac.ru/MCC/PRODUCTS/',
  )
  downloaded_files = []
  for time in [time - SECS_IN_DAY, time, time + SECS_IN_DAY]:
    t = time.as_datetime()
    if GPSTime.from_datetime(datetime.utcnow()) - time > 2*SECS_IN_WEEK:
      try:
        folder_path = t.strftime('%y%j/final/')
        filename = "Sta%i%i.sp3" % (time.week, time.day)
        downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename))
        continue
      except IOError:
        pass
    try:
      folder_path = t.strftime('%y%j/rapid/')
      filename = "Sta%i%i.sp3" % (time.week, time.day)
      downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename))
    except IOError:
      pass
    try:
      folder_path = t.strftime('%y%j/ultra/')
      filename = "Sta%i%i.sp3" % (time.week, time.day)
      downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename))
    except IOError:
      pass
  return downloaded_files


def download_ionex(time, cache_dir):
  cache_subdir = cache_dir + 'ionex/'
  t = time.as_datetime()
  url_bases = (
    'https://github.com/commaai/gnss-data/raw/master/gnss/products/ionex/',
    'https://cddis.nasa.gov/archive/gnss/products/ionex/',
    'ftp://igs.ensg.ign.fr/pub/igs/products/ionosphere/',
    'ftp://gssc.esa.int/gnss/products/ionex/',
  )
  for folder_path in [t.strftime('%Y/%j/')]:
    for filename in [t.strftime("codg%j0.%yi"), t.strftime("c1pg%j0.%yi"), t.strftime("c2pg%j0.%yi")]:
      try:
        filepath = download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.Z')
        return filepath
      except IOError as e:
        last_err = e
  raise last_err


def download_dcb(time, cache_dir):
  cache_subdir = cache_dir + 'dcb/'
  # seem to be a lot of data missing, so try many days
  for time in [time - i*SECS_IN_DAY for i in range(14)]:
    try:
      t = time.as_datetime()
      url_bases = (
        'https://github.com/commaai/gnss-data/raw/master/gnss/products/bias/',
        'https://cddis.nasa.gov/archive/gnss/products/bias/',
        'ftp://igs.ign.fr/pub/igs/products/mgex/dcb/',
      )
      folder_path = t.strftime('%Y/')
      filename = t.strftime("CAS0MGXRAP_%Y%j0000_01D_01D_DCB.BSX")
      filepath = download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.gz')
      return filepath
    except IOError as e:
      last_err = e
  raise last_err


def download_cors_coords(cache_dir):
  cache_subdir = cache_dir + 'cors_coord/'
  url_bases = (
    'ftp://geodesy.noaa.gov/cors/coord/coord_14/',
    'ftp://alt.ngs.noaa.gov/cors/coord/coord_14/'
  )
  file_names = list_dir(url_bases)
  file_names = [file_name for file_name in file_names if file_name.endswith('coord.txt')]
  filepaths = download_files(url_bases, '', cache_subdir, file_names)
  return filepaths


def download_cors_station(time, station_name, cache_dir):
  cache_subdir = cache_dir + 'cors_obs/'
  t = time.as_datetime()
  folder_path = t.strftime('%Y/%j/') + station_name + '/'
  filename = station_name + t.strftime("%j0.%yd")
  url_bases = (
    'ftp://geodesy.noaa.gov/cors/rinex/',
    'ftp://alt.ngs.noaa.gov/cors/rinex/'
  )
  try:
    filepath = download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.gz')
    return filepath
  except IOError:
    print("File not downloaded, check availability on server.")
    return None
