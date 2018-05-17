import pytest
import core.utils.date_utils as date_utils
import pandas as pd
import datetime
import pytz
from toolz import pipe


@pytest.fixture
def utc_offset():
    return datetime.timedelta(0)


class TestDateUtils():

    def test_datetime_utc_timezone(self, utc_offset):
        offset = pipe(
            (2018, 1, 1),
            date_utils.datetime_utc,
            date_utils.offset_utc
        )

        assert offset == utc_offset

    def test_timestamp_strip_ms_timestamp(self):
        dt = datetime.datetime(2018, 1, 1).timestamp()

        assert date_utils.timestamp_strip_ms(dt) == dt / 1000

    def test_timestamp_strip_ms_timestamp_ms(self):
        dt = date_utils.timestamp_ms_short_utc((2018, 1, 1))

        assert date_utils.timestamp_strip_ms(dt) == dt

    def test_date_range_day(self, two_sequential_days):
        date_range = date_utils.date_range(*two_sequential_days, '4h')

        assert date_utils.date_range_length(date_range) == 6

    def test_date_range_hour(self):
        start_dt = datetime.datetime(2018, 1, 1, 1)
        end_dt = datetime.datetime(2018, 1, 1, 2)
        # function should convert '1m' to '1T'
        date_range = date_utils.date_range(start_dt, end_dt, '1m')

        assert date_utils.date_range_length(date_range) == 60

    def test_get_data_range_length(self, two_sequential_days):
        frequency = '4h'
        date_range = date_utils.date_range(*two_sequential_days, frequency)
        data_ranges = date_utils.get_data_range_length(*two_sequential_days,
                                                       frequency)

        assert data_ranges == date_utils.date_range_length(date_range)

    def test_is_minutely_frequency(self):
        assert pipe('1m', date_utils.is_minutely_frequency, bool) == True

    @pytest.mark.parametrize('timeframe, timeframes, seconds', [
        ('15m', 10000, 15 * 60 * 10000),
        ('15T', 1, 15 * 60),
        ('12h', 1, 60 * 60 * 12),
        ('1h', 2, 60 * 60 * 2),
        ('1d', 2, 60 * 60 * 24 * 2),
        ('1s', 1, None)
    ])
    def test_timeframes_to_seconds(self, timeframe, timeframes, seconds):
        assert date_utils.timeframes_to_seconds(timeframe,
                                                timeframes) == seconds

    @pytest.mark.parametrize('date, timeframe, expected', [
        (
            datetime.datetime(2018, 5, 14, 00, 50), '12h',
            datetime.datetime(2018, 5, 14, 12, 50)
        ),
        (
            datetime.datetime(2018, 5, 14, 00, 50, 1, 2), '1m',
            datetime.datetime(2018, 5, 14, 12, 50, 2, 2)
        )
    ])
    def test_add_timeframe_to_date(self, date, timeframe, expected):
        assert date_utils.add_timeframe_to_date(date, timeframe)
