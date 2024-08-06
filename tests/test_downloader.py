import os
import unittest
from dataclasses import dataclass
from itertools import product
from unittest.mock import patch
from parameterized import parameterized

from laika.downloader import download_and_cache_file, download_file, DownloadFailed

@dataclass
class IGSFileTest:
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

  igs_files = [
    IGSFileTest(
      folder_path = '2323/',
      filename = 'IGS0OPSULT_20242021800_02D_15M_ORB.SP3',
      compression= '.gz',
      file_size = 192658,
      cache_dir = '/tmp/gnss/'+'cddis_products'
      ),
    IGSFileTest(
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
    for igs_file in self.igs_files:
      for f in [igs_file.filepath, igs_file.filepath_zipped, igs_file.filepath_attempt]:
        if os.path.exists(f):
          os.remove(f)

  def _download_and_cache_file(self, url_bases, igs_file, *args, **kwargs):
    return download_and_cache_file(
      url_bases, igs_file.folder_path, cache_dir=igs_file.cache_dir, filename=igs_file.filename, compression=igs_file.compression, *args, **kwargs
      )

  @parameterized.expand(product(url_bases, igs_files))
  def test_all_download_protocols(self, url_base, igs_file):
    dat = download_file(url_base, igs_file.folder_path, igs_file.filename_zipped)
    success = dat and len(dat) == igs_file.file_size
    self.assertTrue(success, f"{url_base + igs_file.folder_path + igs_file.filename_zipped} is incorrect size: {0 if not dat else len(dat)}")

  @parameterized.expand(igs_files)
  def test_download_list(self, igs_file):
    file = self._download_and_cache_file(self.url_bases, igs_file)
    self.assertIsNotNone(file)

  @parameterized.expand(igs_files)
  def test_download_list_with_disabled_mirror(self, igs_file):
    file = self._download_and_cache_file((None, "", self.url_bases[0]), igs_file)
    self.assertIsNotNone(file)

  @parameterized.expand(igs_files)
  def test_download_overwrite(self, igs_file):
    file = self._download_and_cache_file(self.url_bases, igs_file)
    self.assertIsNotNone(file)
    # Should overwrite file without error
    file = self._download_and_cache_file(self.url_bases, igs_file, overwrite=True)
    self.assertIsNotNone(file)

  @parameterized.expand(igs_files)
  def test_write_attempt_file_on_error(self, igs_file):
    self.assertFalse(os.path.exists(igs_file.filepath_attempt))

    with patch("laika.downloader.download_file", side_effect=DownloadFailed), self.assertRaises(DownloadFailed):
      self._download_and_cache_file(self.url_bases, igs_file)
      self.assertTrue(os.path.exists(igs_file.filepath_attempt), msg="Attempt file should have been written after exception")

    # Should raise when trying again after failure
    with self.assertRaises(DownloadFailed):
      self._download_and_cache_file(self.url_bases, igs_file)

  @parameterized.expand(igs_files)
  def test_wait_after_failure(self, igs_file):
    # Verify no failure first.
    self._download_and_cache_file(self.url_bases, igs_file)

    # Verify last download fails due failure waiting time.
    with patch("laika.downloader.download_file", side_effect=DownloadFailed), self.assertRaises(DownloadFailed):
      self._download_and_cache_file(self.url_bases, igs_file, overwrite=True)
    with self.assertRaises(DownloadFailed):
      self._download_and_cache_file(self.url_bases, igs_file)


if __name__ == "__main__":
  unittest.main()
