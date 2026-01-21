import os
import unittest
from dataclasses import dataclass
from itertools import product
from unittest.mock import patch
from parameterized import parameterized

from laika.downloader import download_and_cache_file, download_file, DownloadFailed

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
      filename = 'IGS0OPSULT_20242021800_02D_15M_ORB.SP3',
      compression= '.gz',
      file_size = 192658,
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


if __name__ == "__main__":
  unittest.main()
