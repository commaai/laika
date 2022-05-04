import unittest

from laika.helpers import get_constellation, get_prn_from_nmea_id, get_nmea_id_from_prn

SBAS_DATA = [
    ['S01', 33],
    ['S02', 34],
    ['S10', 42],
    ['S22', 54],

    ['S23', 55],
    ['S32', 64],

    ['S33', 120],
    ['S64', 151],

    ['S65', 152],
    ['S71', 158]
]

MAIN_CONSTELLATIONS = [
    ['G01', 1],
    ['G10', 10],
    ['G32', 32],
    ['R01', 65],
    ['R10', 74],
    ['R23', 87],
    ['R24', 88],
    ['R25', 89],
    ['R32', 96],
    ['E01', 301],
    ['E02', 302],
    ['E36', 336],
    ['C01', 201],
    ['C02', 202],
    ['C29', 229],
    ['J01', 193],
    ['J04', 196]
]


class TestConstellationPRN(unittest.TestCase):
    def test_constellation_from_valid_prn(self):
        data = [
            ['G01', 'GPS'],
            ['G10', 'GPS'],
            ['G32', 'GPS'],
            ['R01', 'GLONASS'],
            ['R10', 'GLONASS'],
            ['R23', 'GLONASS'],
            ['R24', 'GLONASS'],
            ['R25', 'GLONASS'],
            ['R32', 'GLONASS'],
            ['E01', 'GALILEO'],
            ['E02', 'GALILEO'],
            ['E36', 'GALILEO'],
            ['C01', 'BEIDOU'],
            ['C02', 'BEIDOU'],
            ['C29', 'BEIDOU'],
            ['J01', 'QZNSS'],
            ['J04', 'QZNSS'],
            ['S01', 'SBAS'],
            ['I01', 'IRNSS']
        ]

        for prn, expected_constellation in data:
            constellation = get_constellation(prn)
            self.assertEqual(constellation, expected_constellation)

    def test_constellation_from_prn_outside_range(self):
        prn = 'G99'
        constellation = get_constellation(prn)
        self.assertEqual(constellation, 'GPS')

    def test_prn_from_nmea_id_for_main_constellations(self):
        data = MAIN_CONSTELLATIONS

        for expected_prn, nmea_id in data:
            prn = get_prn_from_nmea_id(nmea_id)
            self.assertEqual(prn, expected_prn)

    def test_prn_from_nmea_id_for_SBAS(self):
        '''Probably numbering SBAS as single constellation doesn't make
        sense, but programmatically it works the same as for others
        constellations.'''
        data = SBAS_DATA

        for expected_prn, nmea_id in data:
            prn = get_prn_from_nmea_id(nmea_id)
            self.assertEqual(expected_prn, prn)

    def test_nmea_id_from_prn_for_main_constellations(self):
        data = MAIN_CONSTELLATIONS

        for prn, expected_nmea_id in data:
            nmea_id = get_nmea_id_from_prn(prn)
            self.assertEqual(expected_nmea_id, nmea_id)

    def test_nmea_id_from_prn_for_SBAS(self):
        '''Probably numbering SBAS as single constellation doesn't make
        sense, but programmatically it works the same as for others
        constellations.'''
        data = SBAS_DATA

        for prn, expected_nmea_id in data:
            nmea_id = get_nmea_id_from_prn(prn)
            self.assertEqual(expected_nmea_id, nmea_id)

    def test_nmea_id_from_invalid_prn(self):
        # Constellation with unknwown identifier
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'X01')
        # Valid constellation - invalid number
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'G00')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'GAA')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'G33')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'C99')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'R99')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'J99')
