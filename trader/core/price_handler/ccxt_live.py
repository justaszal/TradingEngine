import asyncio
import core.price_handler.utils.candles_utils as candles_utils
import core.utils.date_utils as date_utils
import core.utils.functional as functional
import datetime
import pandas as pd
from core.price_handler.abstract_price_handler import (AbstractBarPriceHandler,
                                                       LivePriceHandler)
from toolz import compose
from core.event import BarEvent
from ccxt import (NetworkError,
                  ExchangeError)


class CCXTLivePriceHandler(AbstractBarPriceHandler, LivePriceHandler):

    def __init__(self, tickers, exchange, events_queue, timeframe='1m',
                 end_date=None):
        self.tickers = tickers
        self.exchange = exchange
        self.events_queue = events_queue
        self.timeframe = timeframe
        self.start_date = datetime.datetime.now()
        self.end_date = end_date
        self.create_bar_event = candles_utils.create_bar_event(
            timeframe=self.timeframe)
        self.tickers_data = compose(dict, zip)(
            self.tickers, map(lambda ticker: pd.DataFrame(), self.tickers)
        )

    def __is_session_time_done(self, now_dt):
        return now_dt > self.end_date if self.end_date else False

    async def __get_candle(self, ticker):
        return await self.exchange.get_candles(
            ticker, self.timeframe, limit=1
        )

    async def __stream_bar_event(self, ticker):
        candles = await self.exchange.get_candles(
            ticker, self.timeframe, limit=1
        )
        # Add candle to tickers_data
        candles_df = self._get_candles_data_frame(ticker, candles)
        self.tickers_data[ticker] = self.tickers_data[ticker].append(
            candles_df
        )
        append_ticker_to_array = functional.append(x=ticker)
        # Create bar event
        return compose(self.create_bar_event, append_ticker_to_array)(
            *candles
        )

    async def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        bar_event = None
        if not self.__is_session_time_done(datetime.datetime.now()):
            try:
                for ticker in self.tickers:
                    bar_event = await self.__stream_bar_event(ticker)
                    await self.events_queue.put(bar_event)
                """
                If next cycle exceeds the limit of session time then
                terminate so consumer whould not wait till next timeframe
                """
                next_now_dt = date_utils.add_timeframe_to_date(
                    datetime.datetime.now(), self.timeframe)

                if self.__is_session_time_done(next_now_dt):
                    await self.events_queue.put(None)
                    bar_event = None
            except (ExchangeError, NetworkError) as e:
                raise ExchangeRequestError(e)
        else:
            await self.events_queue.put(None)

        return True if bar_event else None
