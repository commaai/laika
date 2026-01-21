from datetime import datetime
import unittest

from laika import AstroDog
from laika.ephemeris import EphemerisType
from laika.gps_time import GPSTime
from laika.helpers import ConstellationId


class TestFetchSatInfo(unittest.TestCase):
  def test_fetch_data_from_distant_future(self):
    dog = AstroDog()
    date = GPSTime.from_datetime(datetime(3120, 1, 1))
    self.assertRaises(RuntimeError, dog.get_sat_info, "G01", date)

  def test_get_all_sat_info_gps(self):
    time = GPSTime.from_datetime(datetime(2024, 5, 1, 12, 0, 0))
    all_ephem_types = (EphemerisType.FINAL_ORBIT, EphemerisType.NAV)
    kwargs_list = [
      *[{"valid_const": [ConstellationId.GPS], "valid_ephem_types": ephem_type} for ephem_type in all_ephem_types],
      *[{"valid_const": [ConstellationId.GLONASS], "valid_ephem_types": ephem_type} for ephem_type in all_ephem_types],
      #*[{"valid_const": [ConstellationId.BEIDOU], "valid_ephem_types": ephem_type} for ephem_type in EphemerisType.all_orbits()],
      *[{"valid_const": [ConstellationId.GALILEO], "valid_ephem_types": ephem_type} for ephem_type in (EphemerisType.FINAL_ORBIT,)],
      #*[{"valid_const": [ConstellationId.QZNSS], "valid_ephem_types": ephem_type} for ephem_type in EphemerisType.all_orbits()],
    ]

    for kwargs in kwargs_list:
      dog = AstroDog(**kwargs)
      infos = dog.get_all_sat_info(time)
      self.assertGreater(len(infos), 0, f"No ephemeris found for {kwargs}")


if __name__ == '__main__':
  unittest.main()
