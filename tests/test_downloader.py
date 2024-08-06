import os
import unittest
from dataclasses import dataclass
from unittest.mock import patch

from laika.downloader import download_and_cache_file, download_file, DownloadFailed

@dataclass
class IGSFileTest:
  folder_path: str
  filename: str
  compression: str
  file_size: int

  @property
  def filename_zipped(self):
    return self.filename + self.compression

class TestDownloader(unittest.TestCase):

  def setUp(self) -> None:
    self.cache_dir = '/tmp/gnss/'+'cddis_products'
    self.url_base = (
      'https://raw.githubusercontent.com/commaai/gnss-data/master/gnss/products/',
      'sftp://gdc.cddis.eosdis.nasa.gov/gnss/products/',
      'ftp://igs.ign.fr/pub/igs/products/',
    )
    # test case:
    self.igs_file = IGSFileTest(
      folder_path = '2323/',
      filename = 'IGS0OPSULT_20242021800_02D_15M_ORB.SP3',
      compression= '.gz',
      file_size = 192658
    )

    folder_path_abs = os.path.join(self.cache_dir, self.igs_file.folder_path)

    filepath_zipped = os.path.join(folder_path_abs, self.igs_file.filename_zipped)
    filepath = os.path.join(folder_path_abs, self.igs_file.filename)
    self.filepath_attempt = filepath + '.attempt_time'
    for f in [filepath, filepath_zipped, self.filepath_attempt]:
      if os.path.exists(f):
        os.remove(f)

  def test_all_download_protocols(self):
    for url_base in self.url_base:
      dat = download_file(url_base, self.igs_file.folder_path, self.igs_file.filename_zipped)
      success = dat and len(dat) == self.file_size
      self.assertTrue(success, f"{url_base + self.igs_file.folder_path + self.igs_file.filename_zipped} is incorrect size: {0 if not dat else len(dat)}")

  def test_download_list(self):
    file = download_and_cache_file(
      self.url_base, self.igs_file.folder_path, cache_dir=self.cache_dir, filename=self.igs_file.filename, compression=self.igs_file.compression
      )
    self.assertIsNotNone(file)

  def test_download_list_with_disabled_mirror(self):
    file = download_and_cache_file(
      (None, "", self.url_base[0]), self.igs_file.folder_path, cache_dir=self.cache_dir, filename=self.igs_file.filename, compression=self.igs_file.compression
      )
    self.assertIsNotNone(file)

  def test_download_overwrite(self):
    file = download_and_cache_file(
      self.url_base, self.igs_file.folder_path, cache_dir=self.cache_dir, filename=self.igs_file.filename, compression=self.igs_file.compression
      )
    self.assertIsNotNone(file)
    # Should overwrite file without error
    file = download_and_cache_file(
      self.url_base, self.igs_file.folder_path, cache_dir=self.cache_dir, filename=self.igs_file.filename, compression=self.igs_file.compression, overwrite=True
      )
    self.assertIsNotNone(file)

  def test_write_attempt_file_on_error(self):
    self.assertFalse(os.path.exists(self.filepath_attempt))

    with patch("laika.downloader.download_file", side_effect=DownloadFailed), self.assertRaises(DownloadFailed):
      download_and_cache_file(
        self.url_base, self.igs_file.folder_path, cache_dir=self.cache_dir, filename=self.igs_file.filename, compression=self.igs_file.compression
        )

      self.assertTrue(os.path.exists(self.filepath_attempt), msg="Attempt file should have been written after exception")

    # Should raise when trying again after failure
    with self.assertRaises(DownloadFailed):
      download_and_cache_file(
        self.url_base, self.igs_file.folder_path, cache_dir=self.cache_dir, filename=self.igs_file.filename, compression=self.igs_file.compression
        )

  def test_wait_after_failure(self):
    # Verify no failure first.
    download_and_cache_file(
      self.url_base, self.igs_file.folder_path, cache_dir=self.cache_dir, filename=self.igs_file.filename, compression=self.igs_file.compression
      )

    # Verify last download fails due failure waiting time.
    with patch("laika.downloader.download_file", side_effect=DownloadFailed), self.assertRaises(DownloadFailed):
      download_and_cache_file(
        self.url_base, self.igs_file.folder_path, cache_dir=self.cache_dir, filename=self.igs_file.filename, compression=self.igs_file.compression,
        overwrite=True
        )
    with self.assertRaises(DownloadFailed):
      download_and_cache_file(
        self.url_base, self.igs_file.folder_path, cache_dir=self.cache_dir, filename=self.igs_file.filename, compression=self.igs_file.compression
        )


if __name__ == "__main__":
  unittest.main()
