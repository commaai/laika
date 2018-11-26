import numpy as np
import unittest

from laika.gnss.gps_time import GPSTime, TimeSyncer
from laika.gnss.astro_dog import AstroDog
from datetime import datetime

gps_times_list = [[1950, 415621.0],
    [1895, 455457.0],
    [1882, 443787.0]]

svIds = ['G01', 'G31']#, 'R08']
gps_times = [GPSTime(*gps_time_list) for gps_time_list in gps_times_list]

class TestAstroDog(unittest.TestCase):
  '''
  def test_orbit_new(self):
    dog = AstroDog(pull_orbit=True, cache_dir='/tmp/')
    gps_time = GPSTime.from_datetime(datetime.utcnow())
    for svId in svIds:
      dog.get_sat_info(svId, gps_time)

  def test_nav_only_new(self):
    dog = AstroDog(pull_orbit=False, cache_dir='/tmp/')
    gps_time = GPSTime.from_datetime(datetime.utcnow())
    for svId in svIds:
      dog.get_sat_info(svId, gps_time)

  def test_nav_vs_orbit_now(self):
    dog_orbit = AstroDog(pull_orbit=True, cache_dir='/tmp/')
    dog_nav = AstroDog(pull_orbit=False, cache_dir='/tmp/')
    gps_time = GPSTime.from_datetime(datetime.utcnow())
    for svId in svIds:
      sat_info_nav = dog_nav.get_sat_info(svId, gps_time)
      sat_info_orbit = dog_orbit.get_sat_info(svId, gps_time)
      np.testing.assert_allclose(sat_info_nav[0], sat_info_orbit[0], rtol=0, atol=4)
      np.testing.assert_allclose(sat_info_nav[1], sat_info_orbit[1], rtol=0, atol=.1)
      np.testing.assert_allclose(sat_info_nav[2], sat_info_orbit[2], rtol=0, atol=1e-7)
      np.testing.assert_allclose(sat_info_nav[3], sat_info_orbit[3], rtol=0, atol=1e-11)
  '''
  def test_orbit_old_no_cache(self):
    dog = AstroDog(pull_orbit=True, cache_dir='/tmp/')
    for gps_time in gps_times:
      for svId in svIds:
        dog.get_sat_info(svId, gps_time)

  def test_nav_only_old(self):
    dog = AstroDog(pull_orbit=False)
    for gps_time in gps_times:
      for svId in svIds:
        dog.get_sat_info(svId, gps_time)

  def test_nav_vs_orbit__old(self):
    dog_orbit = AstroDog(pull_orbit=True)
    dog_nav = AstroDog(pull_orbit=False)
    for gps_time in gps_times:
      for svId in svIds:
        sat_info_nav = dog_nav.get_sat_info(svId, gps_time)
        sat_info_orbit = dog_orbit.get_sat_info(svId, gps_time)
        #print 'SVID', svId
        #print 'NAV INFO', sat_info_nav
        #print 'ORBIT INFO', sat_info_orbit
        np.testing.assert_allclose(sat_info_nav[0], sat_info_orbit[0], rtol=0, atol= 4)
        np.testing.assert_allclose(sat_info_nav[1], sat_info_orbit[1], rtol=0, atol=.1)
        np.testing.assert_allclose(sat_info_nav[2], sat_info_orbit[2], rtol=0, atol=1e-7)
        np.testing.assert_allclose(sat_info_nav[3], sat_info_orbit[3], rtol=0, atol=1e-11)

  def test_nav_only_old_no_cache(self):
    dog = AstroDog(pull_orbit=False, cache_dir='/tmp/')
    for gps_time in gps_times:
      for svId in svIds:
        dog.get_sat_info(svId, gps_time)

  def test_orbit_old(self):
    dog = AstroDog(pull_orbit=True)
    for gps_time in gps_times:
      for svId in svIds:
        dog.get_sat_info(svId, gps_time)
if __name__ == "__main__":
  unittest.main()
