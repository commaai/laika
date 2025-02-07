import certifi
import ftplib
import hatanaka
import os
import pycurl
import re
import time
import logging

from datetime import datetime, timedelta
from urllib.parse import urlparse
from io import BytesIO
from ftplib import FTP_TLS, FTP

from atomicwrites import atomic_write

from laika.ephemeris import EphemerisType
from .constants import SECS_IN_HR, SECS_IN_DAY, SECS_IN_WEEK
from .gps_time import GPSTime
from .helpers import ConstellationId

dir_path = os.path.dirname(os.path.realpath(__file__))

# mirror of sftp://gdc.cddis.eosdis.nasa.gov
CDDIS_BASE_URL = os.getenv("CDDIS_BASE_URL", "https://raw.githubusercontent.com/commaai/gnss-data/master")

# mirror of sftp://gdc.cddis.eosdis.nasa.gov/gnss/data/hourly
CDDIS_HOURLY_BASE_URL = os.getenv("CDDIS_HOURLY_BASE_URL", "https://raw.githubusercontent.com/commaai/gnss-data-hourly/master")


class DownloadFailed(Exception):
  pass


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
    for url_base in (url for url in url_bases if url):
      try:
        return f(url_base, *args, **kwargs)
      except DownloadFailed as e:
        logging.warning(e)
    # none of them succeeded
    raise DownloadFailed("Multiple URL failures attempting to pull file(s)")
  return wrapped


def mirror_url(base, path):
  # None means disabled
  return base + path if base else None


def ftp_connect(url):
  parsed = urlparse(url)
  assert parsed.scheme == 'ftp'
  try:
    domain = parsed.netloc
    ftp = ftplib.FTP(domain, timeout=10)
    ftp.login()
  except (OSError, ftplib.error_perm):
    raise DownloadFailed("Could not connect/auth to: " + domain)
  try:
    ftp.cwd(parsed.path)
  except ftplib.error_perm:
    raise DownloadFailed("Permission failure with folder: " + url)
  return ftp


@retryable
def list_dir(url):
  parsed = urlparse(url)
  if parsed.scheme == 'ftp':
    try:
      ftp = ftp_connect(url)
      return ftp.nlst()
    except ftplib.error_perm:
      raise DownloadFailed("Permission failure listing folder: " + url)
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
    logging.debug("pulling from", url_base, "to", filepath)

    if not os.path.isfile(filepath):
      os.makedirs(folder_path_abs, exist_ok=True)
      try:
        ftp.retrbinary('RETR ' + filename, open(filepath, 'wb').write)
      except (ftplib.error_perm):
        raise DownloadFailed("Could not download file from: " + url_base + folder_path + filename)
      except (TimeoutError):
        raise DownloadFailed("Read timed out from: " + url_base + folder_path + filename)
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
      logging.debug("pulling from", url_base, "to", filepath)
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
    logging.warning("some requests stalled, retrying them")
    return http_download_files(url_base, folder_path, cacheDir, filenames)

  return filepaths


def https_download_file(url):
  crl = pycurl.Curl()
  crl.setopt(crl.CAINFO, certifi.where())
  crl.setopt(crl.URL, url)
  crl.setopt(crl.FOLLOWLOCATION, True)
  crl.setopt(crl.SSL_CIPHER_LIST, 'DEFAULT@SECLEVEL=1')
  crl.setopt(crl.COOKIEJAR, '/tmp/cddis_cookies')
  crl.setopt(pycurl.CONNECTTIMEOUT, 10)

  buf = BytesIO()
  crl.setopt(crl.WRITEDATA, buf)
  crl.perform()
  response = crl.getinfo(pycurl.RESPONSE_CODE)
  crl.close()

  if response != 200:
    raise DownloadFailed('HTTPS error ' + str(response))
  return buf.getvalue()


def ftp_download_file(url):
  parsed = urlparse(url)
  is_sftp = parsed.scheme == "sftp"
  try:
    buf = BytesIO()
    with FTP_TLS(parsed.hostname) if is_sftp else FTP(parsed.hostname) as ftp:
      ftp.login(user='anonymous')
      if is_sftp:
        ftp.prot_p()
      ftp.retrbinary('RETR ' + parsed.path, buf.write)
    return buf.getvalue()
  except ftplib.all_errors as e:
    raise DownloadFailed(e)


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
  logging.debug('Downloading ' + url)
  if url.startswith(('http://', 'https://')):
    return https_download_file(url)
  elif url.startswith(('ftp://', 'sftp://')):
    return ftp_download_file(url)
  raise NotImplementedError('Did not find supported url scheme')


def download_and_cache_file_return_first_success(url_bases, folder_and_file_names, cache_dir, compression='', overwrite=False, raise_error=False):
  last_error = None
  for folder_path, filename in folder_and_file_names:
    try:
      file = download_and_cache_file(url_bases, folder_path, cache_dir, filename, compression, overwrite)
      return file
    except DownloadFailed as e:
      last_error = e

  if last_error and raise_error:
    raise last_error


def download_and_cache_file(url_base, folder_path: str, cache_dir: str, filename: str, compression='', overwrite=False):
  filename_zipped = filename + compression
  folder_path_abs = os.path.join(cache_dir, folder_path)
  filepath = str(hatanaka.get_decompressed_path(os.path.join(folder_path_abs, filename)))

  filepath_attempt = filepath + '.attempt_time'

  if os.path.exists(filepath_attempt):
    with open(filepath_attempt) as rf:
      last_attempt_time = float(rf.read())
    if time.time() - last_attempt_time < SECS_IN_HR:
      raise DownloadFailed(f"Too soon to try downloading {folder_path + filename_zipped} from {url_base} again since last attempt")
  if not os.path.isfile(filepath) or overwrite:
    try:
      data_zipped = download_file(url_base, folder_path, filename_zipped)
    except (DownloadFailed, pycurl.error, TimeoutError):
      unix_time = time.time()
      os.makedirs(folder_path_abs, exist_ok=True)
      with atomic_write(filepath_attempt, mode='w', overwrite=True) as wf:
        wf.write(str(unix_time))
      raise DownloadFailed(f"Could not download {folder_path + filename_zipped} from {url_base}")

    os.makedirs(folder_path_abs, exist_ok=True)
    ephem_bytes = hatanaka.decompress(data_zipped)
    try:
      with atomic_write(filepath, mode='wb', overwrite=overwrite) as f:
        f.write(ephem_bytes)
    except FileExistsError:
      # Only happens when same file is downloaded in parallel by another process.
      pass
  return filepath


# Currently, only GPS and Glonass are supported for daily and hourly data.
CONSTELLATION_NASA_CHAR = {ConstellationId.GPS: 'n', ConstellationId.GLONASS: 'g'}


def download_nav(time: GPSTime, cache_dir, constellation: ConstellationId):
  t = time.as_datetime()
  if constellation not in CONSTELLATION_NASA_CHAR:
    return None
  c = CONSTELLATION_NASA_CHAR[constellation]
  if GPSTime.from_datetime(datetime.utcnow()) - time > SECS_IN_DAY:
    url_bases = (
      mirror_url(CDDIS_BASE_URL, '/gnss/data/daily/'),
    )
    filename = t.strftime(f"brdc%j0.%y{c}")
    folder_path = t.strftime(f'%Y/%j/%y{c}/')
    compression = '.gz' if folder_path >= '2020/335/' else '.Z'
    return download_and_cache_file(url_bases, folder_path, cache_dir+'daily_nav/', filename, compression)
  else:
    url_bases = (
      mirror_url(CDDIS_HOURLY_BASE_URL, '/'),
    )
    times = [t, (t - timedelta(hours=1))]
    folder_and_filenames = [(t.strftime('%Y/%j/'), t.strftime(f"hour%j0.%y{c}")) for t in times]
    compression = '.gz' if folder_and_filenames[0][0] >= '2020/336/' else '.Z'
    # always overwrite as this file is appended
    return download_and_cache_file_return_first_success(url_bases,
      folder_and_filenames, cache_dir+'hourly_nav/', compression, overwrite=True)


def download_orbits_gps(time, cache_dir, ephem_types):
  url_bases = (
    mirror_url(CDDIS_BASE_URL, '/gnss/products/'),
    mirror_url(CDDIS_BASE_URL, '/glonass/products/'),
  )

  folder_path = "%i/" % time.week
  filenames = []
  compression = '.gz'

  if time.week < 2238:
    assert EphemerisType.FINAL_ORBIT in ephem_types, f"Only final orbits are available before 2238, {ephem_types}"
    filenames.extend(['COD0MGXFIN_{yyyy}{doy:03d}0000_01D_05M_ORB.SP3'.format(yyyy=time.year, doy=time.doy)])
  else:
    # TODO deal with version number
    ephem_strs =  {
      EphemerisType.FINAL_ORBIT: ['COD0OPSFIN_{yyyy}{doy:03d}0000_01D_05M_ORB.SP3'.format(yyyy=time.year, doy=time.doy)],
      EphemerisType.RAPID_ORBIT: ['COD0OPSRAP_{yyyy}{doy:03d}0000_01D_05M_ORB.SP3'.format(yyyy=time.year, doy=time.doy)],
      EphemerisType.ULTRA_RAPID_ORBIT: ['COD0OPSULT_{yyyy}{doy:03d}{hh}00_02D_05M_ORB.SP3'.format(yyyy=time.year, doy=time.doy, hh=hour) \
        for hour in ['18', '12', '06', '00']],
    }

    # Download filenames in order of quality. Final -> Rapid -> Ultra-Rapid(newest first)
    if EphemerisType.FINAL_ORBIT in ephem_types and GPSTime.from_datetime(datetime.utcnow()) - time > 3 * SECS_IN_WEEK:
      filenames.extend(ephem_strs[EphemerisType.FINAL_ORBIT])
    if EphemerisType.RAPID_ORBIT in ephem_types and GPSTime.from_datetime(datetime.utcnow()) - time > 3 * SECS_IN_DAY:
      filenames.extend(ephem_strs[EphemerisType.RAPID_ORBIT])
    if EphemerisType.ULTRA_RAPID_ORBIT in ephem_types:
      filenames.extend(ephem_strs[EphemerisType.ULTRA_RAPID_ORBIT])

  folder_file_names = [(folder_path, filename) for filename in filenames]
  ret = download_and_cache_file_return_first_success(url_bases, folder_file_names, cache_dir+'cddis_products/', compression=compression)
  print(filenames)
  return ret


def download_ionex(time, cache_dir):
  t = time.as_datetime()
  url_bases = (
    mirror_url(CDDIS_BASE_URL, '/gnss/products/ionex/'),
  )
  folder_path = t.strftime('%Y/%j/')
  # Format date change
  if time >= GPSTime(2238, 0.0):
    filenames = [t.strftime('COD0OPSFIN_%Y%j0000_01D_01H_GIM.INX.gz'),
                 t.strftime('COD0OPSRAP_%Y%j0000_01D_01H_GIM.INX.gz'),
                 t.strftime("c2pg%j0.%yi.Z")]
  else:
    filenames = [t.strftime("codg%j0.%yi.Z"),
                 t.strftime("c1pg%j0.%yi.Z"),
                 t.strftime("c2pg%j0.%yi.Z")]

  folder_file_names = [(folder_path, f) for f in filenames]
  return download_and_cache_file_return_first_success(url_bases, folder_file_names, cache_dir+'ionex/', raise_error=True)


def download_dcb(time, cache_dir):
  filenames = []
  formats = ['CAS0MGXRAP_%Y%j0000_01D_01D_DCB.BSX',
             'CAS0OPSRAP_%Y%j0000_01D_01D_DCB.BIA']
  folder_paths = []
  url_bases = (
    mirror_url(CDDIS_BASE_URL, '/gnss/products/bias/'),
  )
  # seem to be a lot of data missing, so try many days
  for time_step in [time - i * SECS_IN_DAY for i in range(14)]:
    for file_format in formats:
      t = time_step.as_datetime()
      folder_paths.append(t.strftime('%Y/'))
      filenames.append(t.strftime(file_format))
  return download_and_cache_file_return_first_success(url_bases, list(zip(folder_paths, filenames)), cache_dir+'dcb/', compression='.gz', raise_error=True)


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
  t = time.as_datetime()
  folder_path = t.strftime('%Y/%j/') + station_name + '/'
  filename = station_name + t.strftime("%j0.%yd")
  url_bases = (
    'https://geodesy.noaa.gov/corsdata/rinex/',
    'https://alt.ngs.noaa.gov/corsdata/rinex/',
  )
  try:
    filepath = download_and_cache_file(url_bases, folder_path, cache_dir+'cors_obs/', filename, compression='.gz')
    return filepath
  except DownloadFailed:
    logging.warning("File not downloaded, check availability on server.")
    return None
