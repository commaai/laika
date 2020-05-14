import unittest

import numpy as np

from laika.raw_gnss import get_DOP, get_PDOP, get_HDOP, get_VDOP, get_TDOP
from laika.lib.coordinates import geodetic2ecef


class TestDOP(unittest.TestCase):

  def setUp(self):
    self.receiver = geodetic2ecef((0, 0, 0))
    self.satellites = np.array([
      [18935913, -3082759, -18366964],
      [7469795, 22355916, -12240619],
      [11083784, -18179141, 15877221],
      [22862911, 13420911, 1607501]
    ])

  def test_GDOP(self):
    dop = get_DOP(self.receiver, self.satellites)
    self.assertAlmostEqual(dop, 2.352329857908973)

  def test_HDOP(self):
    dop = get_HDOP(self.receiver, self.satellites)
    self.assertAlmostEqual(dop, 1.3418910470124197)

  def test_VDOP(self):
    dop = get_VDOP(self.receiver, self.satellites)
    self.assertAlmostEqual(dop, 1.7378390525714509)

  def test_PDOP(self):
    dop = get_PDOP(self.receiver, self.satellites)
    self.assertAlmostEqual(dop, 2.195622042769321)

  def test_TDOP(self):
    dop = get_TDOP(self.receiver, self.satellites)
    self.assertAlmostEqual(dop, 0.8442153787485294)


if __name__ == "__main__":
  unittest.main()