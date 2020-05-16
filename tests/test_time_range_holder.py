from datetime import datetime
import unittest

from laika.helpers import TimeRangeHolder
from laika.gps_time import GPSTime


class TestTimeRangeHolder(unittest.TestCase):
    def test_empty(self):
        time = GPSTime.from_datetime(datetime(2020, 5, 1, 0, 0, 0))
        holder = TimeRangeHolder()
        self.assertFalse(time in holder)

    def test_one_in_range(self):
        start_time = GPSTime.from_datetime(datetime(2020, 4, 28))
        end_time = GPSTime.from_datetime(datetime(2020, 5, 2))
        time = GPSTime.from_datetime(datetime(2020, 5, 1))

        holder = TimeRangeHolder()
        holder.add(start_time, end_time)

        self.assertTrue(time in holder)

    def test_one_outside_range(self):
        start_time = GPSTime.from_datetime(datetime(2020, 4, 28))
        end_time = GPSTime.from_datetime(datetime(2020, 5, 2))
        time = GPSTime.from_datetime(datetime(2021, 5, 1))

        holder = TimeRangeHolder()
        holder.add(start_time, end_time)

        self.assertFalse(time in holder)

    def test_merge_ranges(self):
        first_range = (GPSTime.from_datetime(datetime(2020, 5, 1)),
                       GPSTime.from_datetime(datetime(2020, 5, 3)))
        second_range = (GPSTime.from_datetime(datetime(2020, 5, 7)),
                       GPSTime.from_datetime(datetime(2020, 5, 9)))
        merge_range = (GPSTime.from_datetime(datetime(2020, 5, 2)),
                       GPSTime.from_datetime(datetime(2020, 5, 8)))
        time = GPSTime.from_datetime(datetime(2020, 5, 5))

        holder = TimeRangeHolder()
        holder.add(*first_range)
        holder.add(*second_range)

        self.assertFalse(time in holder)

        holder.add(*merge_range)

        self.assertTrue(time in holder)

    def test_extend_range_left(self):
        range_ = (GPSTime.from_datetime(datetime(2020, 5, 7)),
                  GPSTime.from_datetime(datetime(2020, 5, 9)))
        merge_range = (GPSTime.from_datetime(datetime(2020, 5, 3)),
                       GPSTime.from_datetime(datetime(2020, 5, 7)))
        time = GPSTime.from_datetime(datetime(2020, 5, 5))

        holder = TimeRangeHolder()
        holder.add(*range_)

        self.assertFalse(time in holder)

        holder.add(*merge_range)

        self.assertTrue(time in holder)

    def test_extend_range_right(self):
        merge_range = (GPSTime.from_datetime(datetime(2020, 5, 7)),
                  GPSTime.from_datetime(datetime(2020, 5, 9)))
        range_ = (GPSTime.from_datetime(datetime(2020, 5, 3)),
                  GPSTime.from_datetime(datetime(2020, 5, 7)))
        time = GPSTime.from_datetime(datetime(2020, 5, 8))

        holder = TimeRangeHolder()
        holder.add(*range_)

        self.assertFalse(time in holder)

        holder.add(*merge_range)

        self.assertTrue(time in holder)