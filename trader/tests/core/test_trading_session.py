import pytest
import asyncio
import core.trading_session as trading_session
import core.errors as errors
from core.trading_session import TradingSession
from unittest.mock import Mock
from core.trading_session import configuration
from core.price_handler.ccxt_live import CCXTLivePriceHandler
from core.price_handler.ccxt_historic import CCXTHistoricPriceHandler


def load_module(path, package=None):
    return None if path == '.ccxt' else path.replace('.', '')


class TestTradingSession:

    @pytest.mark.parametrize('price_handler, session_type,\
        expected_price_handler', [
        (None, 'live', CCXTLivePriceHandler),
        (None, 'backtest', CCXTHistoricPriceHandler),
        ('ccxt_live', 'live', CCXTLivePriceHandler),
        ('ccxt_historic', 'backtest', CCXTHistoricPriceHandler),
        ('ccxt', 'live', CCXTLivePriceHandler)
    ])
    def test_price_handler_configuration(
        self, price_handler, session_type, expected_price_handler, binance
    ):
        """
        TODO: mock CCXTHistoricPriceHandler, CCXTLivePriceHandler and
        __load_price_handler_class() and expose mock stream_next method
        """
        session = TradingSession(
            binance, ['BTC/USDT'], asyncio.Queue(), session_type=session_type,
            price_handler=price_handler
        )
        assert type(session.price_handler) == expected_price_handler

    @pytest.mark.parametrize('session_type, price_handler, expected_error', [
        ('live', {}, errors.PriceHandlerNotFoundError),
        ('wrong session type', 'ccxt', errors.TradingSessionTypeError)
    ])
    def test_price_handler_configuration_error(self, session_type,
                                               price_handler, expected_error,
                                               binance):
        with pytest.raises(expected_error):
            TradingSession(binance, ['BTC/USDT'], asyncio.Queue(),
                           session_type=session_type,
                           price_handler=price_handler)
