import unittest
import time

from laika.ephemeris import EphemerisType
from laika.gps_time import GPSTime
from laika import AstroDog

gps_times_list = [[1950, 415621.0]]

svIds = ['R12']
gps_times = [GPSTime(*gps_time_list) for gps_time_list in gps_times_list]


class TestFailCache(unittest.TestCase):
  def test_no_infinite_pulls(self):
    dog = AstroDog(valid_ephem_types=EphemerisType.all_orbits())
    for gps_time in gps_times:
      for svId in svIds:
        dog.get_sat_info(svId, gps_time)
        t0 = time.time()
        for i in range(1000):
          dog.get_sat_info(svId, gps_time)
          self.assertTrue(time.time() - t0 < 10)

if __name__ == "__main__":
  unittest.main()
