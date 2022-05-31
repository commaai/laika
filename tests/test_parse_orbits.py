from datetime import datetime
import unittest

from laika import AstroDog
from laika.constants import SECS_IN_HR
from laika.ephemeris import EphemerisType
from laika.gps_time import GPSTime


class TestParseOrbits(unittest.TestCase):

  def test_retrieve_specific_orbit_gps(self):
    constellations = ["GPS"]
    self.retrieve_specific_orbit(constellations)

  def test_retrieve_specific_orbit_glonass(self):
    constellations = ["GLONASS"]
    self.retrieve_specific_orbit(constellations)

  def retrieve_specific_orbit(self, constellations):
    available_date = GPSTime.from_datetime(datetime(2020, 5, 1, 12, 0))

    for orbit_type in EphemerisType.orbits():
      dog = AstroDog(valid_const=constellations, valid_ephem_types=orbit_type)
      orbits = dog.download_parse_orbit_data(available_date, skip_before_epoch=available_date-2*SECS_IN_HR)
      self.assertEqual(orbit_type, orbits[0].eph_type, f"Failed to get orbit with type {orbit_type}")


if __name__ == '__main__':
    unittest.main()
