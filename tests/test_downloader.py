import os
import unittest
from dataclasses import dataclass
from itertools import product
from unittest.mock import patch
from parameterized import parameterized

import pycurl

from laika.downloader import download_and_cache_file, download_file, DownloadFailed, https_download_file

@dataclass
class TestFile:
  folder_path: str
  filename: str
  compression: str
  file_size: int
  cache_dir: str

  @property
  def filename_zipped(self):
    return self.filename + self.compression

  @property
  def filepath_zipped(self):
    return os.path.join(self.cache_dir, self.folder_path, self.filename_zipped)

  @property
  def filepath(self):
    return os.path.join(self.cache_dir, self.folder_path, self.filename)

  @property
  def filepath_attempt(self):
    return self.filepath + '.attempt_time'

class TestDownloader(unittest.TestCase):

  files = [
    TestFile(
      folder_path = '2323/',
      filename = 'IGS0OPSFIN_20242000000_01D_15M_ORB.SP3',
      compression= '.gz',
      file_size = 100190,
      cache_dir = '/tmp/gnss/'+'cddis_products'
      ),
    TestFile(
      folder_path = '2103/',
      filename = 'igu21034_18.sp3',
      compression = '.Z',
      file_size = 197513,
      cache_dir = '/tmp/gnss/'+'cddis_products'
    )
  ]

  url_bases = (
    'https://raw.githubusercontent.com/commaai/gnss-data/master/gnss/products/',
    'sftp://gdc.cddis.eosdis.nasa.gov/gnss/products/',
    'ftp://igs.ign.fr/pub/igs/products/',
  )

  def setUp(self) -> None:
    for file in self.files:
      for f in [file.filepath, file.filepath_zipped, file.filepath_attempt]:
        if os.path.exists(f):
          os.remove(f)

  def _download_and_cache_file(self, url_bases, file, *args, **kwargs):
    return download_and_cache_file(
      url_bases, file.folder_path, cache_dir=file.cache_dir, filename=file.filename, compression=file.compression, *args, **kwargs
      )

  @parameterized.expand(product(url_bases, files))
  def test_all_download_protocols(self, url_base, file):
    dat = download_file(url_base, file.folder_path, file.filename_zipped)
    success = dat and len(dat) == file.file_size
    self.assertTrue(success, f"{url_base + file.folder_path + file.filename_zipped} is incorrect size: {0 if not dat else len(dat)}")

  @parameterized.expand([(f,) for f in files])
  def test_download_list(self, file):
    downloaded_file = self._download_and_cache_file(self.url_bases, file)
    self.assertIsNotNone(downloaded_file)

  @parameterized.expand([(f,) for f in files])
  def test_download_list_with_disabled_mirror(self, file):
    downloaded_file = self._download_and_cache_file((None, "", self.url_bases[0]), file)
    self.assertIsNotNone(downloaded_file)

  @parameterized.expand([(f,) for f in files])
  def test_download_overwrite(self, file):
    downloaded_file = self._download_and_cache_file(self.url_bases, file)
    self.assertIsNotNone(downloaded_file)
    # Should overwrite file without error
    downloaded_file = self._download_and_cache_file(self.url_bases, file, overwrite=True)
    self.assertIsNotNone(downloaded_file)

  @parameterized.expand([(f,) for f in files])
  def test_write_attempt_file_on_error(self, file):
    self.assertFalse(os.path.exists(file.filepath_attempt))

    with patch("laika.downloader.download_file", side_effect=DownloadFailed), self.assertRaises(DownloadFailed):
      self._download_and_cache_file(self.url_bases, file)
      self.assertTrue(os.path.exists(file.filepath_attempt), msg="Attempt file should have been written after exception")

    # Should raise when trying again after failure
    with self.assertRaises(DownloadFailed):
      self._download_and_cache_file(self.url_bases, file)

  @parameterized.expand([(f,) for f in files])
  def test_wait_after_failure(self, file):
    # Verify no failure first.
    self._download_and_cache_file(self.url_bases, file)

    # Verify last download fails due failure waiting time.
    with patch("laika.downloader.download_file", side_effect=DownloadFailed), self.assertRaises(DownloadFailed):
      self._download_and_cache_file(self.url_bases, file, overwrite=True)
    with self.assertRaises(DownloadFailed):
      self._download_and_cache_file(self.url_bases, file)


class FakeCurl:
  """Minimal pycurl.Curl stand-in to test cipher-list fallback without network."""

  # pycurl exposes option constants as instance attributes; mirror the ones used.
  CAINFO = pycurl.CAINFO
  URL = pycurl.URL
  FOLLOWLOCATION = pycurl.FOLLOWLOCATION
  SSL_CIPHER_LIST = pycurl.SSL_CIPHER_LIST
  COOKIEJAR = pycurl.COOKIEJAR
  WRITEDATA = pycurl.WRITEDATA

  def __init__(self, fail_first_perform_with=None, payload=b"data"):
    self.fail_first_perform_with = fail_first_perform_with
    self.payload = payload
    self.cipher_lists = []
    self.perform_calls = 0
    self.buf = None

  def setopt(self, opt, val):
    if opt == pycurl.SSL_CIPHER_LIST:
      self.cipher_lists.append(val)
    elif opt == pycurl.WRITEDATA:
      self.buf = val

  def perform(self):
    self.perform_calls += 1
    if self.perform_calls == 1 and self.fail_first_perform_with is not None:
      code, msg = self.fail_first_perform_with
      raise pycurl.error(code, msg)
    self.buf.write(self.payload)

  def getinfo(self, opt):
    return 200

  def close(self):
    pass


class TestHttpsDownloadCipherFallback(unittest.TestCase):
  # commaai/laika#62: '@SECLEVEL=1' is rejected by OpenSSL >= 1.1.1t / LibreSSL
  # with pycurl.error 59, which must trigger a fallback, not a crash.

  def test_falls_back_on_ssl_cipher_error(self):
    fake = FakeCurl(fail_first_perform_with=(pycurl.E_SSL_CIPHER, "failed setting cipher list"))
    with patch("laika.downloader.pycurl.Curl", return_value=fake):
      self.assertEqual(https_download_file("https://example.com/file"), b"data")
    self.assertEqual(fake.cipher_lists, ["DEFAULT", "DEFAULT@SECLEVEL=1"])

  def test_no_retry_on_unrelated_error(self):
    fake = FakeCurl(fail_first_perform_with=(pycurl.E_COULDNT_CONNECT, "couldn't connect"))
    with patch("laika.downloader.pycurl.Curl", return_value=fake):
      with self.assertRaises(pycurl.error):
        https_download_file("https://example.com/file")
    self.assertEqual(fake.cipher_lists, ["DEFAULT"])
    self.assertEqual(fake.perform_calls, 1)

  def test_plain_default_cipher_list_first_try(self):
    fake = FakeCurl()
    with patch("laika.downloader.pycurl.Curl", return_value=fake):
      self.assertEqual(https_download_file("https://example.com/file"), b"data")
    self.assertEqual(fake.cipher_lists, ["DEFAULT"])
    self.assertEqual(fake.perform_calls, 1)


if __name__ == "__main__":
  unittest.main()
