import certifi
import ftplib
import hatanaka
import os
import urllib.request
import pycurl
import re
import time
import tempfile
import socket

from datetime import datetime
from urllib.parse import urlparse
from io import BytesIO

from .constants import SECS_IN_HR, SECS_IN_DAY, SECS_IN_WEEK
from .gps_time import GPSTime
from .helpers import ConstellationId

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
    ftp = ftplib.FTP(domain, timeout=10)
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
  parsed = urlparse(url)
  if parsed.scheme == 'ftp':
    try:
      ftp = ftp_connect(url)
      return ftp.nlst()
    except ftplib.error_perm:
      raise IOError("Permission failure listing folder: " + url)
  else:
    # just connect and do simple url parsing
    listing = https_download_file(url)
    urls = re.findall(b"<a href=\"([^\"]+)\">", listing)
    # decode the urls to normal strings. If they are complicated paths, ignore them
    return [name.decode("latin1") for name in urls if name and b"/" not in name[1:]]

def ftp_download_files(url_base, folder_path, cacheDir, filenames):
  """
  Like download file, but more of them. Keeps a persistent FTP connection open
  to be more efficient.
  """
  folder_path_abs = os.path.join(cacheDir, folder_path)

  ftp = ftp_connect(url_base + folder_path)

  filepaths = []
  for filename in filenames:
    # os.path.join will be dumb if filename has a leading /
    # if there is a / in the filename, then it's using a different folder
    filename = filename.lstrip("/")
    if "/" in filename:
      continue
    filepath = os.path.join(folder_path_abs, filename)
    print("pulling from", url_base, "to", filepath)

    if not os.path.isfile(filepath):
      os.makedirs(folder_path_abs, exist_ok=True)
      try:
        ftp.retrbinary('RETR ' + filename, open(filepath, 'wb').write)
      except (ftplib.error_perm):
        raise IOError("Could not download file from: " + url_base + folder_path + filename)
      except (socket.timeout):
        raise IOError("Read timed out from: " + url_base + folder_path + filename)
      filepaths.append(filepath)
    else:
      filepaths.append(filepath)
  return filepaths

def http_download_files(url_base, folder_path, cacheDir, filenames):
  """
  Similar to ftp_download_files, attempt to download multiple files faster than
  just downloading them one-by-one.
  Returns a list of filepaths instead of the raw data
  """
  folder_path_abs = os.path.join(cacheDir, folder_path)

  def write_function(disk_path, handle):
    def do_write(data):
      open(disk_path, "wb").write(data)
    return do_write

  fetcher = pycurl.CurlMulti()
  fetcher.setopt(pycurl.M_PIPELINING, 3)
  fetcher.setopt(pycurl.M_MAX_HOST_CONNECTIONS, 64)
  fetcher.setopt(pycurl.M_MAX_TOTAL_CONNECTIONS, 64)
  filepaths = []
  for filename in filenames:
    # os.path.join will be dumb if filename has a leading /
    # if there is a / in the filename, then it's using a different folder
    filename = filename.lstrip("/")
    if "/" in filename:
      continue
    filepath = os.path.join(folder_path_abs, filename)
    if not os.path.isfile(filepath):
      print("pulling from", url_base, "to", filepath)
      os.makedirs(folder_path_abs, exist_ok=True)
      url_path = url_base + folder_path + filename
      handle = pycurl.Curl()
      handle.setopt(pycurl.URL, url_path)
      handle.setopt(pycurl.CONNECTTIMEOUT, 10)
      handle.setopt(pycurl.WRITEFUNCTION, write_function(filepath, handle))
      fetcher.add_handle(handle)
      filepaths.append(filepath)

  requests_processing = len(filepaths)
  timeout = 10.0  # after 10 seconds of nothing happening, restart
  deadline = time.time() + timeout
  while requests_processing and time.time() < deadline:
    while True:
      ret, cur_requests_processing = fetcher.perform()
      if ret != pycurl.E_CALL_MULTI_PERFORM:
        _, success, failed = fetcher.info_read()
        break
    if requests_processing > cur_requests_processing:
      deadline = time.time() + timeout
      requests_processing = cur_requests_processing

    if fetcher.select(1) < 0:
      continue

  # if there are downloads left to be done, repeat, and don't overwrite
  _, requests_processing = fetcher.perform()
  if requests_processing > 0:
    print("some requests stalled, retrying them")
    return http_download_files(url_base, folder_path, cacheDir, filenames)

  return filepaths



def https_download_file(url):
  if 'nasa.gov/' not in url:
    netrc_path = None
    f = None
  elif os.path.isfile(dir_path + '/.netrc'):
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
  crl.setopt(crl.SSL_CIPHER_LIST, 'DEFAULT@SECLEVEL=1')
  crl.setopt(crl.COOKIEJAR, '/tmp/cddis_cookies')
  crl.setopt(pycurl.CONNECTTIMEOUT, 10)
  if netrc_path is not None:
    crl.setopt(crl.NETRC_FILE, netrc_path)
    crl.setopt(crl.NETRC, 2)

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
  urlf = urllib.request.urlopen(url, timeout=10)
  data_zipped = urlf.read()
  urlf.close()
  return data_zipped


@retryable
def download_files(url_base, folder_path, cacheDir, filenames):
  parsed = urlparse(url_base)
  if parsed.scheme == 'ftp':
    return ftp_download_files(url_base, folder_path, cacheDir, filenames)
  else:
    return http_download_files(url_base, folder_path, cacheDir, filenames)


@retryable
def download_file(url_base, folder_path, filename_zipped):
  url = url_base + folder_path + filename_zipped
  print('Downloading ' + url)
  if url.startswith('https'):
    return https_download_file(url)
  if url.startswith('ftp'):
    return ftp_download_file(url)
  raise NotImplementedError('Did find ftp or https preamble')


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
    os.makedirs(folder_path_abs, exist_ok=True)

    try:
      data_zipped = download_file(url_base, folder_path, filename_zipped)
    except (IOError, pycurl.error, socket.timeout):
      unix_time = time.time()
      tmp_dir = cacheDir + '/tmp'
      os.makedirs(tmp_dir, exist_ok=True)
      with tempfile.NamedTemporaryFile(delete=False, dir=tmp_dir) as fout:
        fout.write(str.encode(str(unix_time)))
      os.replace(fout.name, filepath + '.attempt_time')
      raise IOError(f"Could not download {folder_path + filename_zipped} from {url_base} ")


    with open(filepath_zipped, 'wb') as wf:
      wf.write(data_zipped)

    filepath = str(hatanaka.decompress_on_disk(filepath_zipped))
  return filepath


# Currently, only GPS and Glonass are supported for daily and hourly data.
CONSTELLATION_NASA_CHAR = {ConstellationId.GPS: 'n', ConstellationId.GLONASS: 'g'}


def download_nav(time: GPSTime, cache_dir, constellation: ConstellationId):
  t = time.as_datetime()
  try:
    if constellation not in CONSTELLATION_NASA_CHAR:
      return None
    c = CONSTELLATION_NASA_CHAR[constellation]
    if GPSTime.from_datetime(datetime.utcnow()) - time > SECS_IN_DAY:
      url_bases = (
        'https://github.com/commaai/gnss-data/raw/master/gnss/data/daily/',
        'https://cddis.nasa.gov/archive/gnss/data/daily/',
      )
      cache_subdir = cache_dir + 'daily_nav/'
      filename = t.strftime(f"brdc%j0.%y{c}")
      folder_path = t.strftime(f'%Y/%j/%y{c}/')
      compression = '.gz' if folder_path >= '2020/335/' else '.Z'
      return download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression=compression)
    elif constellation == ConstellationId.GPS:
        url_base = 'https://cddis.nasa.gov/archive/gnss/data/hourly/'
        cache_subdir = cache_dir + 'hourly_nav/'
        filename = t.strftime(f"hour%j0.%y{c}")
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
    folder_path = "%i/" % time.week
    filenames = []
    if GPSTime.from_datetime(datetime.utcnow()) - time > 3*SECS_IN_WEEK:
      filenames.append("igs%i%i.sp3" % (time.week, time.day))
    filenames.extend([
      "igr%i%i.sp3" % (time.week, time.day),
      "igu%i%i_18.sp3" % (time.week, time.day),
      "igu%i%i_12.sp3" % (time.week, time.day),
      "igu%i%i_06.sp3" % (time.week, time.day),
      "igu%i%i_00.sp3" % (time.week, time.day),
    ])
    for filename in filenames:
      try:
        downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.Z'))
        break
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
  for t_step in [time - SECS_IN_DAY, time, time + SECS_IN_DAY]:
    t = t_step.as_datetime()
    folder_paths = []
    filename = "Sta%i%i.sp3" % (t_step.week, t_step.day)
    if GPSTime.from_datetime(datetime.utcnow()) - t_step > 2*SECS_IN_WEEK:
      folder_paths.append(t.strftime('%y%j/final/'))
    folder_paths.append(t.strftime('%y%j/rapid/'))
    folder_paths.append(t.strftime('%y%j/ultra/'))
    for folder_path in folder_paths:
      try:
        downloaded_files.append(download_and_cache_file(url_bases, folder_path, cache_subdir, filename))
        break
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
    'https://geodesy.noaa.gov/corsdata/coord/coord_14/',
    'https://alt.ngs.noaa.gov/corsdata/coord/coord_14/',
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
    'https://geodesy.noaa.gov/corsdata/rinex/',
    'https://alt.ngs.noaa.gov/corsdata/rinex/',
  )
  try:
    filepath = download_and_cache_file(url_bases, folder_path, cache_subdir, filename, compression='.gz')
    return filepath
  except IOError:
    print("File not downloaded, check availability on server.")
    return None
