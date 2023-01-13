import os
import unittest
from unittest.mock import patch

from laika.downloader import download_and_cache_file, download_file, DownloadFailed


class TestDownloader(unittest.TestCase):

  def setUp(self) -> None:
    self.cache_dir = '/tmp/gnss/'+'cddis_products'
    self.url_base = (
      'https://github.com/commaai/gnss-data/raw/master/gnss/products/',
      'sftp://gdc.cddis.eosdis.nasa.gov/gnss/products/',
      'ftp://igs.ign.fr/pub/igs/products/',
    )
    self.folder_path = '2103/'
    self.filename = 'igu21034_18.sp3'
    self.filename_zipped = self.filename + '.Z'

    folder_path_abs = os.path.join(self.cache_dir, self.folder_path)

    filepath_zipped = os.path.join(folder_path_abs, self.filename_zipped)
    filepath = os.path.join(folder_path_abs, self.filename)
    self.filepath_attempt = filepath + '.attempt_time'
    for f in [filepath, filepath_zipped, self.filepath_attempt]:
      if os.path.exists(f):
        os.remove(f)

  def test_all_download_protocols(self):
    for url_base in self.url_base:
      dat = download_file(url_base, self.folder_path, self.filename_zipped)
      self.assertTrue(dat and len(dat) == 197513, f"{url_base + self.folder_path + self.filename_zipped} is incorrect size: {0 if not dat else len(dat)}")

  def test_download(self):
    file = download_and_cache_file(self.url_base, self.folder_path, cache_dir=self.cache_dir, filename=self.filename, compression='.Z')
    self.assertIsNotNone(file)

  def test_download_overwrite(self):
    file = download_and_cache_file(self.url_base, self.folder_path, cache_dir=self.cache_dir, filename=self.filename, compression='.Z')
    self.assertIsNotNone(file)
    # Should overwrite file without error
    file = download_and_cache_file(self.url_base, self.folder_path, cache_dir=self.cache_dir, filename=self.filename, compression='.Z', overwrite=True)
    self.assertIsNotNone(file)

  def test_write_attempt_file_on_error(self):
    self.assertFalse(os.path.exists(self.filepath_attempt))

    with patch("laika.downloader.download_file", side_effect=DownloadFailed):
      with self.assertRaises(DownloadFailed):
        download_and_cache_file(self.url_base, self.folder_path, cache_dir=self.cache_dir, filename=self.filename, compression='.Z')

      self.assertTrue(os.path.exists(self.filepath_attempt), msg="Attempt file should have been written after exception")

    # Should raise when trying again after failure
    with self.assertRaises(DownloadFailed):
      download_and_cache_file(self.url_base, self.folder_path, cache_dir=self.cache_dir, filename=self.filename, compression='.Z')

  def test_wait_after_failure(self):
    # Verify no failure first.
    download_and_cache_file(self.url_base, self.folder_path, cache_dir=self.cache_dir, filename=self.filename, compression='.Z')

    # Verify last download fails due failure waiting time.
    with patch("laika.downloader.download_file", side_effect=DownloadFailed):
      with self.assertRaises(DownloadFailed):
        download_and_cache_file(self.url_base, self.folder_path, cache_dir=self.cache_dir, filename=self.filename, compression='.Z', overwrite=True)
    with self.assertRaises(DownloadFailed):
      download_and_cache_file(self.url_base, self.folder_path, cache_dir=self.cache_dir, filename=self.filename, compression='.Z')


if __name__ == "__main__":
  unittest.main()
