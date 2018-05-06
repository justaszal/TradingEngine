import pytest
import asyncio
import tests.test_utils.common as test_utils
from functools import reduce
from toolz import curry
from core.strategy.EMA_cross import EMACrossStrategy


class TestEMACross:
    ema_cross = EMACrossStrategy(['BTC/USDT', 'ETH/USDT'], asyncio.Queue())

    def test_EMA_cross_initialization_tickers_storage(self):
        # pytest.skip()
        is_type_ndarray = test_utils.is_object_type_name(name='ndarray')
        btc_bars = self.ema_cross.tickers_storage['BTC/USDT']['bars']
        btc_index = self.ema_cross.tickers_storage['BTC/USDT']['index']
        btc_is_bought = self.ema_cross.tickers_storage['BTC/USDT']['is_bought']
        eth_bars = self.ema_cross.tickers_storage['ETH/USDT']['bars']
        eth_index = self.ema_cross.tickers_storage['ETH/USDT']['index']
        eth_is_bought = self.ema_cross.tickers_storage['ETH/USDT']['is_bought']

        is_not_bought = not btc_is_bought and not eth_is_bought
        zero_indexes = btc_index == 0 and eth_index == 0

        assert reduce(
            lambda is_ndarray, x: is_type_ndarray(
                x) if is_ndarray is True else False,
            [btc_bars, eth_bars],
            True
        ) and is_not_bought and zero_indexes
