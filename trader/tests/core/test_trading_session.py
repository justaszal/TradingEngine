import pytest
import asyncio
import core.errors as errors
from core.trading_session import TradingSession
from core.price_handler.ccxt_live import CCXTLivePriceHandler
from core.price_handler.ccxt_historic import CCXTHistoricPriceHandler
from core.strategy.EMA_cross import EMACrossStrategy


loop = asyncio.get_event_loop()
queue = asyncio.Queue()
tickers = ['BTC/USDT']
ema_strategy = EMACrossStrategy(tickers, queue)


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
        session = loop.run_until_complete(TradingSession.create(
            binance, tickers, queue, ema_strategy, 1000,
            session_type=session_type, price_handler=price_handler
        ))
        assert type(session.price_handler) == expected_price_handler

    @pytest.mark.parametrize('session_type, price_handler, expected_error', [
        ('live', {}, errors.PriceHandlerNotFoundError),
        ('wrong session type', 'ccxt', errors.TradingSessionTypeError)
    ])
    def test_price_handler_configuration_error(self, session_type,
                                               price_handler, expected_error,
                                               binance):
        with pytest.raises(expected_error):
            loop.run_until_complete(TradingSession.create(
                binance, tickers, queue, ema_strategy, 1000,
                session_type=session_type, price_handler=price_handler
            ))
