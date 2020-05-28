import numpy as np
import unittest

from laika.gps_time import GPSTime
from laika import AstroDog

gps_times_list = [[1950, 415621.0],
    [1895, 455457.0],
    [1885, 443787.0]]

svIds = ['G01', 'G31', 'R08']
gps_times = [GPSTime(*gps_time_list) for gps_time_list in gps_times_list]


class TestAstroDog(unittest.TestCase):
  '''
  def test_nav_vs_orbit_now(self):
    dog_orbit = AstroDog(pull_orbit=True)
    dog_nav = AstroDog(pull_orbit=False)
    gps_time = GPSTime.from_datetime(datetime.utcnow()) - SECS_IN_DAY*2
    for svId in svIds:
      sat_info_nav = dog_nav.get_sat_info(svId, gps_time)
      sat_info_orbit = dog_orbit.get_sat_info(svId, gps_time)
      np.testing.assert_allclose(sat_info_nav[0], sat_info_orbit[0], rtol=0, atol=5)
      np.testing.assert_allclose(sat_info_nav[1], sat_info_orbit[1], rtol=0, atol=.1)
      np.testing.assert_allclose(sat_info_nav[2], sat_info_orbit[2], rtol=0, atol=1e-7)
      np.testing.assert_allclose(sat_info_nav[3], sat_info_orbit[3], rtol=0, atol=1e-11)
  '''
  def test_nav_vs_orbit__old(self):
    dog_orbit = AstroDog(pull_orbit=True)
    dog_nav = AstroDog(pull_orbit=False)
    for gps_time in gps_times:
      for svId in svIds:
        sat_info_nav = dog_nav.get_sat_info(svId, gps_time)
        sat_info_orbit = dog_orbit.get_sat_info(svId, gps_time)
        np.testing.assert_allclose(sat_info_nav[0], sat_info_orbit[0], rtol=0, atol=5)
        np.testing.assert_allclose(sat_info_nav[1], sat_info_orbit[1], rtol=0, atol=.1)
        np.testing.assert_allclose(sat_info_nav[2], sat_info_orbit[2], rtol=0, atol=1e-7)
        np.testing.assert_allclose(sat_info_nav[3], sat_info_orbit[3], rtol=0, atol=1e-11)


if __name__ == "__main__":
  unittest.main()
