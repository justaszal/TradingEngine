from core.price_handler.ccxt_historic import CCXTHistoricPriceHandler
from core.price_handler.ccxt_live import CCXTLivePriceHandler
from core.price_handler.base import AbstractPriceHandler
from toolz import first, compose
from core.errors import (TradingSessionTypeError,
                         PriceHandlerNotFoundError)
import asyncio
import core.utils.date_utils as date_utils
import core.configuration as configuration


class TradingSession:
    """
    Enscapsulates the settings and components for
    carrying out either a backtest or live trading session.
    """

    def __init__(self, exchange, tickers, events_queue, start_date=None,
                 end_date=None, timeframe="1h", session_type="backtest",
                 price_handler=None):
        """
        Args:
            exchange: exchange object
            tickers: list of tickers
            events_queue: events to process inside event loop
                event types: TICK, BAR
            start_date: datetime object, start of loop
            end_date: datetime object, end of loop
            timeframe: candle timeframe (default: {"1h"})
            session_type: backtest/live (default: {"backtest"})
            price_handler (None, optional): streams price data to event loop
        """
        self.exchange = exchange
        self.tickers = tickers
        self.events_queue = events_queue
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.session_type = session_type
        self.price_handler = price_handler
        self.__config_session()

    def __config_session(self):
        """
        Session configuration
        """
        self.heartbeat = (
            date_utils.timeframes_to_seconds(self.timeframe)
            if self.session_type == 'live'
            else None
        )

        self.__set_price_handler(self.price_handler)

    def __set_price_handler(self, price_handler):
        price_handler_args = (
            self.tickers, self.exchange, self.events_queue, self.timeframe,
            self.start_date, self.end_date
        ) if self.session_type == 'backtest' else (
            self.tickers, self.exchange, self.events_queue, self.timeframe,
            self.end_date
        ) if self.session_type == 'live' else None

        if price_handler_args is None:
            raise TradingSessionTypeError(session_type=self.session_type)

        if self.price_handler is None:
            if self.session_type == 'backtest':
                self.price_handler = CCXTHistoricPriceHandler(
                    *price_handler_args)
            elif self.session_type == 'live':
                self.price_handler = CCXTLivePriceHandler(*price_handler_args)
        elif isinstance(self.price_handler, str):
            price_handler_class = self.__load_price_handler_class()
            self.price_handler = price_handler_class(*price_handler_args)
        elif not isinstance(self.price_handler, AbstractPriceHandler):
            raise PriceHandlerNotFoundError(
                price_handler=self.price_handler)

    def __load_price_handler_class(self):
        return compose(first, configuration.load_module_classes,
                       self.__load_price_module
                       )(self.price_handler)[1]

    def __load_price_module(self, module_name):
        price_handler_module = configuration.load_module(
            '.' + module_name, 'core.price_handler'
        )

        if price_handler_module is None:
            suffix = (self.session_type if self.session_type == 'live'
                      else 'historic')
            price_handler_module = configuration.load_module(
                '.' + module_name + '_' + suffix, 'core.price_handler'
            )

        return price_handler_module

    async def __stream_events(self):
        while True:
            event = await self.price_handler.stream_next()
            """
            Price handler returns None when iterator is empty in backtest
            mode
            """
            if event is None:
                break

            await asyncio.sleep(self.heartbeat or 0)

    async def __process_events(self):
        while True:
            try:
                event = self.events_queue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(1 if self.heartbeat else 0)
            else:
                if event is None:
                    break

    def run_session(self):
        tasks = asyncio.gather(self.__stream_events(), self.__process_events())
        self.exchange.loop.run_until_complete(tasks)
