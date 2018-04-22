import pytest
import datetime
import asyncio
import core.utils.date_utils as date_utils
from core.exchange.ccxt_exchange import CCXT
from unittest.mock import Mock
from toolz import curry, compose
from random import randint
from functools import reduce
from core.exchange.exchange_errors import (ExchangeNotFoundError,
                                           InvalidHistoryTimeframeError)


@curry
def append(arr, x):
    arr.append(x)
    return arr


async def fetch_ohlcv(symbol, timeframe, since, limit=1000):
    return reduce(
        lambda data_set, ohlcv: append(
            data_set,
            [1, 1, 1, 1, 1]),
        range(limit if limit < 1000 else 1000), []
    )


def days_generator_2018_01(*args):
    """Generate a list of given days

    Args:
        *args: days

    Returns:
        List: datetime objects with date 2018-01-X
    """
    return reduce(
        lambda days, day: append(
            days,
            datetime.datetime(2018, 1, day)
        ),
        args,
        []
    )


async def noop(*args):
    await asyncio.sleep(0)


@pytest.fixture(scope="module")
def binance(request, markets):
    CCXT = request.module.CCXT
    exchange = CCXT('binance')
    exchange.markets = markets['binance']
    exchange.load_markets = Mock(side_effect=noop)
    exchange.api.fetch_ohlcv = Mock(side_effect=fetch_ohlcv)

    request.addfinalizer(lambda: exchange.close())
    return exchange


def setup_module(module):
    CCXT.load_markets = Mock(side_effect=noop)


class TestCCXTExchange():

    def test_CCXT_ExchangeNotFoundError(self):
        with pytest.raises(ExchangeNotFoundError):
            CCXT('non-existing exchange name')

    @pytest.mark.parametrize('timeframe, two_sequential_days, limit,\
                              expected_limit',
                             [
                                 ('1H', 0, None, None),
                                 ('1H', 0, 30, 30),
                                 ('1H', 1, 30, 30),
                                 ('1H', None, None, 24),
                                 ('1H', None, 5, 5),
                                 ('1H', None, 30, 24)
                             ],
                             indirect=['two_sequential_days'])
    def test_get_fech_ohlcv_limit(self, timeframe, two_sequential_days, limit,
                                  expected_limit, binance):
        assert binance.get_fech_ohlcv_limit(timeframe,
                                            # array of start date and end date
                                            *two_sequential_days,
                                            limit=limit,
                                            ) == expected_limit

    @pytest.mark.parametrize('timeframe, start_dt, end_dt, limit,\
                             expected_since_date',
                             [
                                 ('4h', None, datetime.datetime(2018, 1, 2),
                                  1, 1514843985600),

                             ])
    def test_get_since_date(self, timeframe, start_dt, end_dt, limit,
                            expected_since_date, binance):
        assert binance.get_since_date(
            timeframe, start_dt, end_dt, limit=limit
        ) == expected_since_date

    def test_CCXT_constructor_loads_markets(self):
        binance = CCXT('binance')
        binance.close()
        assert binance.load_markets.called

    @pytest.mark.parametrize('symbol, timeframe, dates, expected_candles',
                             [
                                 ('BTC/USDT', '15m',
                                  days_generator_2018_01(1, 14),
                                  # 15min -> 4 * 24 = 96
                                  # 15min -> 96 * 13 = 1248
                                  1248),
                                 ('BTC/USDT', '1h',
                                  days_generator_2018_01(1, 2),
                                  24),
                                 ('BTC/USDT', '1d',
                                  days_generator_2018_01(1, 2),
                                  1)
                             ])
    def test_get_candles_api_parameters(self, symbol, timeframe,
                                        dates, expected_candles, binance):
        candles = compose(binance.loop.run_until_complete)(
            binance.get_candles(symbol, timeframe, *dates)
        )
        assert len(candles) == expected_candles

    def test_get_candles_InvalidHistoryTimeframeError(self, binance):
        with pytest.raises(InvalidHistoryTimeframeError):
            compose(binance.loop.run_until_complete)(
                binance.get_candles('BTC/USDT', '1D',
                                    days_generator_2018_01(1, 2),
                                    1)
            )
