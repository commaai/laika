from datetime import datetime
import unittest

from laika import AstroDog
from laika.gps_time import GPSTime


class TestFetchSatInfo(unittest.TestCase):
  def test_fetch_data_from_distant_future(self):
    dog = AstroDog()
    date = GPSTime.from_datetime(datetime(3120, 1, 1))
    self.assertRaises(RuntimeError, dog.get_sat_info, "G01", date)

  def test_no_block_satellite_when_get_info_from_not_available_period(self):
    '''If you first fetch satellite info from period when navigation data
    isn't available and next from period when navigation data are available
    then you should get correct result'''

    prn = "C03"
    constellations = ["GPS", "BEIDOU"]
    available_date = GPSTime.from_datetime(datetime(2020, 5, 1, 12, 0))
    not_available_date = GPSTime.from_datetime(datetime(2000, 1, 1))

    dog = AstroDog(pull_orbit=True, valid_const=constellations)
    sat_info = dog.get_sat_info(prn, not_available_date)
    self.assertIsNone(sat_info)
    sat_info = dog.get_sat_info(prn, available_date)
    self.assertIsNotNone(sat_info)

  def test_get_all_sat_info_gps(self):
    time = GPSTime.from_datetime(datetime(2020, 5, 1, 12, 0, 0))
    kwargs_list = [
        {"valid_const": ["GPS"], "pull_orbit": True},
        {"valid_const": ["GPS"], "pull_orbit": False},
        {"valid_const": ["GLONASS"], "pull_orbit": True},
        {"valid_const": ["GLONASS"], "pull_orbit": False},
        {"valid_const": ["BEIDOU"], "pull_orbit": True},
        {"valid_const": ["GALILEO"], "pull_orbit": True},
        {"valid_const": ["QZNSS"], "pull_orbit": True}
    ]

    for kwargs in kwargs_list:
        dog = AstroDog(**kwargs)
        infos = dog.get_all_sat_info(time)
        self.assertGreater(len(infos), 0)


if __name__ == '__main__':
    unittest.main()
