import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from laika.dgps import get_closest_station_names


def _station(pos):
  return [datetime(2005, 1, 1, tzinfo=timezone.utc), list(pos), [0.0, 0.0, 0.0]]


STATIONS = {
  'AAA': _station([0.0, 0.0, 0.0]),
  'BBB': _station([1000.0, 0.0, 0.0]),
  'CCC': _station([2000.0, 0.0, 0.0]),
}


class TestGetClosestStationNames(unittest.TestCase):
  # commaai/laika#114: cKDTree fills neighbors beyond max_distance with an
  # out-of-bounds idx, which used to raise a cryptic IndexError.

  def _call(self, pos, **kwargs):
    with patch("laika.dgps.load_cors_station_positions", return_value=STATIONS):
      return get_closest_station_names(pos, cache_dir="/tmp/gnss/", **kwargs)

  def test_returns_only_stations_within_max_distance(self):
    names = self._call([500.0, 0.0, 0.0], k=5, max_distance=100000)
    self.assertEqual(set(names), {'AAA', 'BBB', 'CCC'})

  def test_filters_out_of_range_stations(self):
    names = self._call([500.0, 0.0, 0.0], k=5, max_distance=1200)
    self.assertEqual(set(names), {'AAA', 'BBB'})

  def test_raises_clear_error_when_no_station_in_range(self):
    # CORS only covers the US; a receiver in Europe has no station nearby
    with self.assertRaisesRegex(ValueError, "No CORS station within"):
      self._call([4_000_000.0, 500_000.0, 4_800_000.0], k=8, max_distance=100000)

  def test_k_equals_1(self):
    names = self._call([100.0, 0.0, 0.0], k=1, max_distance=100000)
    self.assertEqual(len(names), 1)
    self.assertIn(names[0], {'AAA', 'BBB', 'CCC'})


if __name__ == "__main__":
  unittest.main()
