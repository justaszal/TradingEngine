import pytest
import datetime
import asyncio
import tests.test_utils.common as test_utils
from unittest.mock import Mock
from core.exchange.ccxt_exchange import CCXT


@pytest.fixture(scope='session')
def binance(request, markets):
    exchange = CCXT('binance')
    exchange.markets = markets['binance']
    exchange.load_markets = Mock(side_effect=test_utils.noop_async)
    exchange.api.fetch_ohlcv = Mock(side_effect=test_utils.fetch_ohlcv)
    request.addfinalizer(lambda: exchange.close())
    return exchange


@pytest.fixture(scope='session')
def two_sequential_days(request):
    """Return array of days of 2018 year


    Args:
        request (Object): which day to return

    Returns:
        Returns two days or one depending whether parameter is passed
        Array: [start_dt, end_dt]
    """
    dates = [
        datetime.datetime(2018, 1, 1),
        datetime.datetime(2018, 1, 2)
    ]

    return ([dates[request.param]] if
            hasattr(request, 'param') and
            request.param is not None else
            dates)


@pytest.fixture(scope='session')
def markets(request):
    return {
        'binance': {
            'BTC/USDT': {},
            'ETH/USDT': {}
        }
    }
