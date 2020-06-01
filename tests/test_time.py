import numpy as np
import unittest

from laika.gps_time import GPSTime, TimeSyncer, gpst_to_utc, utc_to_gpst
from datetime import datetime

datetimes_strings = ['1985-10-10 19:27:01',
        '2002-04-27 22:22:06',
        '1986-01-03 06:30:57',
        '2019-09-15 19:30:33',
        '2005-12-06 14:54:22',
        '2008-05-13 08:52:57',
        '2016-01-17 12:50:05',
        '2002-04-08 12:28:19',
        '1998-10-23 06:42:34',
        '2019-01-18 03:16:27']
datetimes = [datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S') for dt_str in datetimes_strings]

gps_times_list = [[300, 415621.0],
    [1163, 598926.0],
    [312, 455457.0],
    [2071, 70233.0],
    [1352, 226462.0],
    [1479, 204777.0],
    [1880, 46205.0],
    [1161, 131299.0],
    [980, 456154.0],
    [2036, 443787.0]]
gps_times = [GPSTime(*gps_time_list) for gps_time_list in gps_times_list]

class TestTime(unittest.TestCase):

  def test_gps_time_dt_conversion(self):
    for dt in datetimes:
      double_converted_dt = GPSTime.from_datetime(dt).as_datetime()
      delta_sec = (dt - double_converted_dt).total_seconds()
      np.testing.assert_allclose(0, delta_sec, rtol=0, atol=1e-10)

    for gps_time, dt in zip(gps_times, datetimes):
      delta_sec = gps_time - GPSTime.from_datetime(dt)
      np.testing.assert_allclose(0, delta_sec, rtol=0, atol=1e-10)

    for gps_time in gps_times:
      double_converted_gps_time = GPSTime.from_datetime(gps_time.as_datetime())
      delta_sec = gps_time - double_converted_gps_time
      np.testing.assert_allclose(0, delta_sec, rtol=0, atol=1e-10)

  def test_gps_time_week_rollover(self):
    for gps_time in gps_times:
      gps_time_plus_week = gps_time + 3600*24*7
      gps_time_minus_week = gps_time - 3600*24*7
      np.testing.assert_allclose(gps_time_plus_week.tow, gps_time.tow, rtol=0, atol=1e-10)
      np.testing.assert_allclose(gps_time_plus_week.week - 1, gps_time.week, rtol=0, atol=1e-10)
      np.testing.assert_allclose(gps_time_minus_week.tow, gps_time.tow, rtol=0, atol=1e-10)
      np.testing.assert_allclose(gps_time_minus_week.week + 1, gps_time.week, rtol=0, atol=1e-10)

  def test_gps_time_subtraction_addition(self):
    for gps_time in gps_times:
      secs = 436
      gps_time_plus_secs = gps_time + secs
      gps_time_minus_secs = gps_time - secs
      delta_sec_plus_gps = gps_time - gps_time_plus_secs
      delta_sec_plus_dt = (gps_time.as_datetime() - gps_time_plus_secs.as_datetime()).total_seconds()
      delta_sec_minus_gps = gps_time - gps_time_minus_secs
      delta_sec_minus_dt = (gps_time.as_datetime() - gps_time_minus_secs.as_datetime()).total_seconds()
      np.testing.assert_allclose(delta_sec_plus_dt, delta_sec_plus_gps, rtol=0, atol=1e-10)
      np.testing.assert_allclose(delta_sec_minus_dt, delta_sec_minus_gps, rtol=0, atol=1e-10)

  def test_syncer(self):
    ref_mono_time = 509045.61126174999
    ref_gps_time = GPSTime(1989, 425928.390)
    syncer = TimeSyncer(ref_mono_time, ref_gps_time)

    secs =  23432.643534
    delta = syncer.gps2mono(syncer.mono2gps(ref_mono_time + secs)) - ref_mono_time
    np.testing.assert_allclose(secs, delta, rtol=0, atol=1e-3)

    # real world test check accurate to 1ms
    delta = GPSTime(1989, 425939.390) - syncer.mono2gps(509056.61195720872)
    np.testing.assert_allclose(0, delta, rtol=0, atol=1e-3)

  def test_utc_converter(self):

    datetimes_strings = ['2008-04-27 22:22:06',
                         '2012-05-13 08:52:57',
                         '2012-09-17 12:50:05',
                         '2016-04-08 12:28:19',
                         '2017-10-23 06:42:34',
                         '2018-01-18 03:16:27',
                         '2017-07-01 00:00:05']
    gps_times = [GPSTime.from_datetime(datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')) for dt_str in datetimes_strings]
    np.testing.assert_allclose((gps_times[0] - gpst_to_utc(gps_times[0])), 14, rtol=0, atol=1e-3)
    np.testing.assert_allclose((gps_times[1] - gpst_to_utc(gps_times[1])), 15, rtol=0, atol=1e-3)
    np.testing.assert_allclose((gps_times[2] - gpst_to_utc(gps_times[2])), 16, rtol=0, atol=1e-3)
    np.testing.assert_allclose((gps_times[3] - gpst_to_utc(gps_times[3])), 17, rtol=0, atol=1e-3)
    np.testing.assert_allclose((gps_times[4] - gpst_to_utc(gps_times[4])), 18, rtol=0, atol=1e-3)
    np.testing.assert_allclose((gps_times[5] - gpst_to_utc(gps_times[5])), 18, rtol=0, atol=1e-3)
    np.testing.assert_allclose((gps_times[6] - gpst_to_utc(gps_times[6])), 17, rtol=0, atol=1e-3)

    np.testing.assert_allclose((gps_times[5] - utc_to_gpst(gpst_to_utc(gps_times[5]))), 0, rtol=0, atol=1e-3)
    np.testing.assert_allclose((gps_times[6] - utc_to_gpst(gpst_to_utc(gps_times[6]))), 0, rtol=0, atol=1e-3)


if __name__ == "__main__":
  unittest.main()
