import core.utils.strings as strings
import core.utils.math_utils as math_utils
import pandas as pd
import datetime
import pytz
import math
import re
from toolz import pipe, curry
from functools import lru_cache


def timestamp_ms_short(dt):
    """Strip microseconds from timestamp

    Example 1451599200.0 -> 1451599200

    Args:
        dt (datetime): datetime object

    Returns:
        String: short version of timestamp
    """
    return pipe(dt, timestamp_ms, math.floor)


def timestamp_ms(dt):
    return dt.timestamp() * 1000


@lru_cache(4)
def get_timezone(timezone):
    return pytz.timezone(timezone)


@curry
def localize(timezone, dt):
    return timezone.localize(dt, is_dst=True)


def localize_utc(dt):
    return pipe('UTC', get_timezone, localize)(dt)


@curry
def normalize(timezone, dt):
    return timezone.normalize(dt)


def normalize_utc(dt):
    return pipe('UTC', get_timezone, normalize)(dt)


def normalize_datetime_utc(dt):
    return pipe(dt, localize_utc, normalize_utc)


def datetime_wrapper(args):
    return datetime.datetime(*args)


def datetime_utc(args):
    return pipe(args, datetime_wrapper, normalize_datetime_utc)


def timestamp_ms_short_utc(dt):
    """Make UTC timestamp and strip milliseconds

    Args:
        dt (Tuple): format: YY:M:D HH:mm:ss:ms

    Returns:
        String: timestamp
    """
    return pipe(dt, datetime_utc, timestamp_ms_short)


@curry
def offset(timezone, dt):
    return get_timezone(timezone).utcoffset(dt)


def offset_utc(dt):
    return offset('UTC')(dt)


def timestamp_strip_ms(timestamp):
    now_timestamp = datetime.datetime.now().timestamp()

    return timestamp if now_timestamp < timestamp else timestamp / 1000


def timestamp_short(timestamp):
    now_timestamp = datetime.datetime.now().timestamp()

    return timestamp if now_timestamp > timestamp else timestamp / 1000


def date_range(start_date, end_date, freq, periods=None):
    return pd.date_range(
        start_date,
        end_date,
        # 'm' which stands for minute is equivalent to 'T' in pandas
        freq=freq.replace('m', 'T'),
        periods=periods
    )


def date_range_length(datetime_index, periods=None):
    """Get length of date_range list

    pd.date_range result of date_range is inclusive. Therefore last
    timeframe does not fit in the time interval calculated in date_range
    function.

    Args:
        t (DatetimeIndex): list of datetime objects

    Returns:
        Int: date_range count
    """
    length = len(datetime_index)
    return length if periods else length - 1


def get_data_range_length(start_date, end_date, freq, periods=None):
    datetime_index = date_range(start_date, end_date, freq, periods)

    return date_range_length(datetime_index, periods)


def timeframes_to_seconds(timeframe, timeframes=1):
    t = pipe(timeframe, strings.first_number, int, math_utils.mul(timeframes))

    return (
        minutes_to_seconds(t) if is_minutely_frequency(timeframe) else
        hours_to_seconds(t) if is_hourly_frequency(timeframe) else
        days_to_seconds(t) if is_daily_frequency(timeframe) else None
    )


@curry
def add_timeframe_to_date(date, timeframe):
    timeframe_seconds = timeframes_to_seconds(timeframe)
    offset = datetime.timedelta(seconds=timeframe_seconds)
    return date + offset


def minutes_to_seconds(t):
    return t * 60


def hours_to_seconds(t):
    return t * 3600


def days_to_seconds(t):
    return t * 86400


def is_minutely_frequency(frequency):
    # T represents minute in pandas library
    return re.search('m|T', frequency)


def is_hourly_frequency(frequency):
    return re.search('h|H', frequency)


def is_daily_frequency(frequency):
    return re.search('d|D', frequency)
