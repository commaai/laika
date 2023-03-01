import numpy as np
from tqdm.auto import tqdm
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
import laika.opt as opt


class TestPositioning(unittest.TestCase):

  @unittest.skip("Takes way too long for CI. Can be used for debugging")
  def test_station_position_long(self):
    self.run_station_position(-1)

  def test_station_position_short(self):
    self.run_station_position(10)

  def run_station_position(self, length):
    dog = AstroDog()
    # Building this cache takes forever just copy it from repo
    cache_directory = '/tmp/gnss/cors_coord/'
    os.makedirs('/tmp/gnss/', exist_ok=True)
    os.makedirs(cache_directory, exist_ok=True)

    examples_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../examples')
    copyfile(os.path.join(examples_directory, 'cors_station_positions'), os.path.join(cache_directory, 'cors_station_positions'))

    station_name = 'sc01'
    time = GPSTime.from_datetime(datetime(2020, 1, 11))
    slac_rinex_obs_file = download_cors_station(time, station_name, dog.cache_dir)
    obs_data = RINEXFile(slac_rinex_obs_file)
    sc01_exact_position = get_station_position('sc01')

    rinex_meas_grouped = raw.read_rinex_obs(obs_data)
    # Select small sample out of ~2800 to reduce computation time
    rinex_meas_grouped = rinex_meas_grouped[:length]
    rinex_corr_grouped = []
    for meas in tqdm(rinex_meas_grouped):
      proc = raw.process_measurements(meas, dog=dog)
      corr = raw.correct_measurements(proc, sc01_exact_position, dog=dog)
      rinex_corr_grouped.append(corr)

    # Using laika's WLS solver we can now calculate position
    # fixes for every epoch (every 30s) over 24h.
    ests = []
    for corr in tqdm(rinex_corr_grouped):
      ret = opt.calc_pos_fix(corr)
      if len(ret) > 0:
        fix, _, _ = ret
        ests.append(fix)
    ests = np.array(ests)

    mean_fix = np.mean(ests[:, :3], axis=0)
    np.testing.assert_allclose(mean_fix, sc01_exact_position, rtol=0, atol=1)


if __name__ == "__main__":
  unittest.main()
