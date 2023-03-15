import numpy as np
import unittest

from laika.ephemeris import EphemerisType, read_prn_data
from laika.gps_time import GPSTime
from laika import AstroDog

gps_times_list = [[1999, 415621.0],
                  [2045, 455457.0],
                  [1985, 443787.0]]

svIds = ['G01', 'G31', 'R08']
gps_times = [GPSTime(*gps_time_list) for gps_time_list in gps_times_list]


class TestAstroDog(unittest.TestCase):
  '''
  def test_nav_vs_orbit_now(self):
    dog_orbit = AstroDog(valid_ephem_types=EphemerisType.orbits())
    dog_nav = AstroDog(valid_ephem_types=EphemerisType.NAV)
    gps_time = GPSTime.from_datetime(datetime.utcnow()) - SECS_IN_DAY*2
    for svId in svIds:
      sat_info_nav = dog_nav.get_sat_info(svId, gps_time)
      sat_info_orbit = dog_orbit.get_sat_info(svId, gps_time)
      np.testing.assert_allclose(sat_info_nav[0], sat_info_orbit[0], rtol=0, atol=5)
      np.testing.assert_allclose(sat_info_nav[1], sat_info_orbit[1], rtol=0, atol=.1)
      np.testing.assert_allclose(sat_info_nav[2], sat_info_orbit[2], rtol=0, atol=1e-7)
      np.testing.assert_allclose(sat_info_nav[3], sat_info_orbit[3], rtol=0, atol=1e-11)
  '''

  def test_nav_vs_orbit_old(self):
    dog_orbit = AstroDog(valid_ephem_types=EphemerisType.all_orbits())
    dog_nav = AstroDog(valid_ephem_types=EphemerisType.NAV)
    for gps_time in gps_times:
      for svId in svIds:
        sat_info_nav = dog_nav.get_sat_info(svId, gps_time)
        assert sat_info_nav is not None
        sat_info_orbit = dog_orbit.get_sat_info(svId, gps_time)
        assert sat_info_orbit is not None
        dog_orbit.get_delay(svId, gps_time, np.array([-2703115.2660, -4291768.3500, 3854247.9590]))
        np.testing.assert_allclose(sat_info_nav[0], sat_info_orbit[0], rtol=0, atol=5)
        np.testing.assert_allclose(sat_info_nav[1], sat_info_orbit[1], rtol=0, atol=.1)
        np.testing.assert_allclose(sat_info_nav[2], sat_info_orbit[2], rtol=0, atol=1e-7)
        np.testing.assert_allclose(sat_info_nav[3], sat_info_orbit[3], rtol=0, atol=1e-11)

  def test_read_prn_data(self):
    prn = 'G01'
    deg = 16

    def get_single_measurement(t):
      return [(EphemerisType.ULTRA_RAPID_ORBIT, GPSTime(0,0), "filename.filetype"), GPSTime(week=2177, tow=172800.0 + t), -22481344.405, -14485178.376, -554329.557, 0.000555129133]

    data = {prn: [get_single_measurement(t * 900) for t in range(deg + 1)]}
    data[prn][0][5] = 0.01
    # Verify no error
    ephems = read_prn_data(data, prn, deg=deg, deg_t=1)
    self.assertEqual(1, len(ephems))

    # should return empty list because of one faulty satellite
    data[prn][0][5] = 1.
    ephems = read_prn_data(data, prn, deg=deg, deg_t=1)
    self.assertEqual(0, len(ephems))


if __name__ == "__main__":
  unittest.main()
