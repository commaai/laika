import unittest

from laika.helpers import get_constellation, get_nmea_id_from_prn, get_prn_from_nmea_id
from laika.helpers import ConstellationId

MAIN_CONSTELLATIONS = [
    ['G01', 1],
    ['G10', 10],
    ['G32', 32],

    ['S01', 33],
    ['S02', 34],
    ['S10', 42],
    ['S22', 54],
    ['S23', 55],
    ['S32', 64],
    ['S33', 120],
    ['S64', 151],
    ['S65', 152],
    ['S71', 158],

    ['R01', 65],
    ['R10', 74],
    ['R23', 87],
    ['R24', 88],
    ['R25', 89],
    ['R32', 96],

    ['J01', 193],
    ['J04', 196],
    ['J08', 200],

    ['C01', 201],
    ['C02', 202],
    ['C35', 235],

    ['E01', 301],
    ['E02', 302],
    ['E36', 336],

    ['C36', 401],
    ['C72', 437],
]


class TestConstellationPRN(unittest.TestCase):
    def test_constellation_from_valid_prn(self):
        data = [
            ['G01', ConstellationId.GPS],
            ['G10', ConstellationId.GPS],
            ['G32', ConstellationId.GPS],
            ['R01', ConstellationId.GLONASS],
            ['R10', ConstellationId.GLONASS],
            ['R23', ConstellationId.GLONASS],
            ['R24', ConstellationId.GLONASS],
            ['R25', ConstellationId.GLONASS],
            ['R32', ConstellationId.GLONASS],
            ['E01', ConstellationId.GALILEO],
            ['E02', ConstellationId.GALILEO],
            ['E36', ConstellationId.GALILEO],
            ['C01', ConstellationId.BEIDOU],
            ['C02', ConstellationId.BEIDOU],
            ['C29', ConstellationId.BEIDOU],
            ['J01', ConstellationId.QZNSS],
            ['J04', ConstellationId.QZNSS],
            ['S01', ConstellationId.SBAS],
            ['I01', ConstellationId.IRNSS]
        ]

        for prn, expected_constellation in data:
            constellation = get_constellation(prn)
            self.assertEqual(expected_constellation, constellation)

    def test_constellation_from_prn_outside_range(self):
        prn = 'G99'
        constellation = get_constellation(prn)
        self.assertEqual(ConstellationId.GPS, constellation)

    def test_prn_from_nmea_id_for_main_constellations(self):
        data = MAIN_CONSTELLATIONS

        for expected_prn, nmea_id in data:
            prn = get_prn_from_nmea_id(nmea_id)
            self.assertEqual(expected_prn, prn)

    def test_nmea_id_from_prn_for_main_constellations(self):
        data = MAIN_CONSTELLATIONS

        for prn, expected_nmea_id in data:
            nmea_id = get_nmea_id_from_prn(prn)
            self.assertEqual(expected_nmea_id, nmea_id)

    def test_nmea_id_from_invalid_prn(self):
        # Constellation with unknown identifier
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'X01')
        # Valid constellation - invalid number
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'G00')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'GAA')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'G33')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'C99')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'R99')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'J99')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'C00')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'C73')

    def test_prn_from_invalid_nmeaid(self):
      self.assertRaises(ValueError, get_prn_from_nmea_id, 97)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 119)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 159)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 172)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 183)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 192)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 236)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 300)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 367)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 400)
      self.assertRaises(ValueError, get_prn_from_nmea_id, 438)

if __name__ == "__main__":
  unittest.main()

