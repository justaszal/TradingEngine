import asyncio
import core.price_handler.utils.candles_utils as candles_utils
import core.utils.date_utils as date_utils
import datetime
from .base import AbstractPriceHandler
from toolz import compose
from core.event import BarEvent


class CCXTLivePriceHandler(AbstractPriceHandler):

    def __init__(self, tickers, exchange, events_queue, timeframe='1m',
                 end_dt=None):
        super().__init__(tickers, exchange, events_queue, timeframe)
        self.end_dt = end_dt
        self.create_bar_event = candles_utils.create_bar_event(
            timeframe=self.timeframe)

    def is_session_time_done(self, now_dt):
        return now_dt > self.end_dt if self.end_dt else False

    async def stream_bar_event(self, ticker):
        return compose(self.create_bar_event)(
            *await self.exchange.get_candles(
                ticker, self.timeframe, limit=1
            )
        )

    async def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        bar_event = None
        if not self.is_session_time_done(datetime.datetime.now()):
            try:
                for ticker in self.tickers:
                    bar_event = await self.stream_bar_event(ticker)
                    await self.events_queue.put(bar_event)
                """
                If next cycle exceeds the limit of session time then
                terminate so consumer whould not wait till next timeframe
                """
                next_now_dt = date_utils.add_timeframe_to_date(
                    datetime.datetime.now(), self.timeframe)

                if self.is_session_time_done(next_now_dt):
                    await self.events_queue.put(None)
                    bar_event = None
            except (ExchangeError, NetworkError) as e:
                raise ExchangeRequestError(e)
        else:
            await self.events_queue.put(None)

        return True if bar_event else None
