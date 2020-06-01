import unittest

from laika.helpers import get_constellation, get_prn_from_nmea_id, \
                          get_nmea_id_from_prn, NMEA_ID_RANGES


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

    def test_constellation_from_prn_with_invalid_identifier(self):
        prn = '?01'

        self.assertWarns(UserWarning, get_constellation, prn)
        self.assertIsNone(get_constellation(prn))

    def test_constellation_from_prn_outside_range(self):
        prn = 'G99'
        constellation = get_constellation(prn)
        self.assertEqual(constellation, 'GPS')

    def test_prn_from_nmea_id_for_main_constellations(self):
        data = [
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

        for expected_prn, nmea_id in data:
            prn = get_prn_from_nmea_id(nmea_id)
            self.assertEqual(prn, expected_prn)

    def test_prn_from_nmea_id_for_SBAS(self):
        '''Probably numbering SBAS as single constellation doesn't make
        a sense, but programatically it works the same as for others
        constellations.'''
        data = [
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

        for expected_prn, nmea_id in data:
            prn = get_prn_from_nmea_id(nmea_id)
            self.assertEqual(prn, expected_prn)

    def test_prn_from_invalid_nmea_id(self):
        data = [
            (-1,  "?-1"),
            (0,   "?0"),
            (100, "?100"),
            (160, "?160"),
            (190, "?190"),
            (300, "?300")
        ]

        for nmea_id, expected_prn in data:
            self.assertWarns(UserWarning, get_prn_from_nmea_id, nmea_id)
            self.assertEqual(get_prn_from_nmea_id(nmea_id), expected_prn)

        self.assertRaises(TypeError, get_prn_from_nmea_id, None)
        self.assertRaises(TypeError, get_prn_from_nmea_id, '1')

    def test_nmea_id_from_prn_for_main_constellations(self):
        data = [
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

        for prn, expected_nmea_id in data:
            nmea_id = get_nmea_id_from_prn(prn)
            self.assertEqual(nmea_id, expected_nmea_id)

    def test_nmea_id_from_prn_for_SBAS(self):
        '''Probably numbering SBAS as single constellation doesn't make
        a sense, but programatically it works the same as for others
        constellations.'''
        data = [
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

        for prn, expected_nmea_id in data:
            nmea_id = get_nmea_id_from_prn(prn)
            self.assertEqual(nmea_id, expected_nmea_id)

    def test_nmea_id_from_invalid_prn(self):
        # Special nknown constellation - valid number
        self.assertEqual(1, get_nmea_id_from_prn('?01'))
        self.assertEqual(-1, get_nmea_id_from_prn('?-1'))
        # Special nknwon constellation - invalid number
        self.assertRaises(ValueError, get_nmea_id_from_prn, '???')
        # Constellation with unknwon identifier
        self.assertRaises(NotImplementedError, get_nmea_id_from_prn, 'X01')
        # Valid constellation - invalid number
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'G00')
        self.assertRaises(ValueError, get_nmea_id_from_prn, 'GAA')
        self.assertRaises(NotImplementedError, get_nmea_id_from_prn, 'G33')
        self.assertRaises(NotImplementedError, get_nmea_id_from_prn, 'C99')
        self.assertRaises(NotImplementedError, get_nmea_id_from_prn, 'R99')
        self.assertRaises(NotImplementedError, get_nmea_id_from_prn, 'J99')
        # None
        self.assertRaises(TypeError, get_nmea_id_from_prn, None)

    def test_nmea_ranges_are_valid(self):
        last_end = 0
        for entry in NMEA_ID_RANGES:
            self.assertIn('range', entry)
            self.assertIn('constellation', entry)
            range_ = entry['range']
            self.assertEqual(len(range_), 2)
            start, end = range_
            self.assertLessEqual(start, end)
            self.assertLess(last_end, start)
            last_end = end
