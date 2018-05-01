from core.price_handler.ccxt_historic import CCXTHistoricPriceHandler
import asyncio
import core.utils.date_utils as date_utils


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
            if self.session_type == "live"
            else None
        )

        if self.price_handler is None and self.session_type == "backtest":
            self.price_handler = CCXTHistoricPriceHandler(
                self.tickers, self.exchange, self.events_queue,
                self.timeframe, self.start_date, self.end_date
            )

    async def stream_events(self):
        while True:
            event = await self.price_handler.stream_next()
            """
            Price handler returns None when iterator is empty in backtest
            mode
            """
            if event is None:
                break

            await asyncio.sleep(self.heartbeat or 0)

    async def process_events(self):
        while True:
            try:
                event = self.events_queue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(1 if self.heartbeat else 0)
            else:
                if event is None:
                    break

    def run_session(self):
        tasks = asyncio.gather(self.stream_events(), self.process_events())
        self.exchange.loop.run_until_complete(tasks)
