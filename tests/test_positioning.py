import numpy as np
from tqdm import tqdm
import unittest
from laika import AstroDog
from shutil import copyfile
import os
from datetime import datetime
from laika.gps_time import GPSTime
from laika.downloader import download_cors_station
from laika.rinex_file import RINEXFile
from laika.dgps import get_station_position
import laika.raw_gnss as raw


class TestPositioning(unittest.TestCase):

  @unittest.skip("Takes way too long to download for ci")
  def test_station_position(self):
    print('WARNING THIS TAKE CAN TAKE A VERY LONG TIME THE FIRST RUN TO DOWNLOAD')
    dog = AstroDog()
    # Building this cache takes forever just copy it from repo
    cache_directory = '/tmp/gnss/cors_coord/'
    try:
      os.mkdir('/tmp/gnss/')
    except OSError:
      pass

    try:
      os.mkdir(cache_directory)
    except OSError:
      pass

    examples_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../examples')
    copyfile(os.path.join(examples_directory, 'cors_station_positions'), os.path.join(cache_directory, 'cors_station_positions'))

    station_name = 'sc01'
    time = GPSTime.from_datetime(datetime(2020, 1, 11))
    slac_rinex_obs_file = download_cors_station(time, station_name, dog.cache_dir)
    obs_data = RINEXFile(slac_rinex_obs_file)
    sc01_exact_position = get_station_position('sc01')

    rinex_meas_grouped = raw.read_rinex_obs(obs_data)
    rinex_corr_grouped = []
    for meas in tqdm(rinex_meas_grouped):
      # proc = raw.process_measurements(meas, dog=dog)
      corr = raw.correct_measurements(meas, sc01_exact_position, dog=dog)
      rinex_corr_grouped.append(corr)

    # Using laika's WLS solver we can now calculate position
    # fixes for every epoch (every 30s) over 24h.
    ests = []
    for corr in tqdm(rinex_corr_grouped[:]):
      fix, _ = raw.calc_pos_fix(corr)
      ests.append(fix)
    ests = np.array(ests)

    mean_fix = np.mean(ests[:, :3], axis=0)
    np.testing.assert_allclose(mean_fix, sc01_exact_position, rtol=0, atol=1)


if __name__ == "__main__":
  unittest.main()
