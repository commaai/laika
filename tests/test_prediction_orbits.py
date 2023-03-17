from datetime import datetime
import unittest

from laika import AstroDog
from laika.constants import SECS_IN_HR
from laika.ephemeris import EphemerisType
from laika.gps_time import GPSTime
from laika.helpers import ConstellationId

class TestPredictionOrbits(unittest.TestCase):

  def test_gps(self):
    available_date = GPSTime.from_datetime(datetime(2020, 5, 1, 12))
    dog = AstroDog(valid_const=(ConstellationId.GPS,), valid_ephem_types=EphemerisType.ULTRA_RAPID_ORBIT)
    dog.get_orbit_data(available_date, only_predictions=True)
    self.assertGreater(len(dog.orbits.keys()), 0)
    self.assertTrue(available_date in dog.orbit_fetched_times)

  def test_gps_and_glonass_2022(self):
    # Test GPS and GLONASS separately from the first date that GLONASS Ultra-Rapid prediction orbits were available
    available_date = GPSTime.from_datetime(datetime(2022, 1, 29, 11, 31))
    for t in range(0, 24, 3):
      check_date = available_date + t * SECS_IN_HR
      for const in [ConstellationId.GPS, ConstellationId.GLONASS]:
        dog = AstroDog(valid_const=(const,), valid_ephem_types=EphemerisType.ULTRA_RAPID_ORBIT)
        dog.get_orbit_data(check_date, only_predictions=True)
        self.assertGreater(len(dog.orbits.keys()), 0)
        self.assertTrue(check_date in dog.orbit_fetched_times)


if __name__ == '__main__':
  unittest.main()
