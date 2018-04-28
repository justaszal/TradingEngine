import pandas as pd
import queue
import asyncio
from functools import reduce
from toolz import compose, curry
from core.exchange.ccxt_exchange import CCXT
from .base import AbstractPriceHandler
from core.event import BarEvent


class CCXTHistoricPriceHandler(AbstractPriceHandler):
    """
    CCXTHistoricKlinesPriceHandler is designed to fetch historic price then
    produce a dataframe of cryptocurrency exchange Open-High-Low-Close-Volume
    (OHLCV) data for each requested financial instrument and stream those to
    the provided events queue as bar events.

    Attributes:
        tickers (List): tickers e.g. ['BTC/USDT']
        exchange (CCXT): cryptocurrency exhange ccxt object
        events_queue (Queue): events queue consumed by trading engine
        timeframe (String): candlestick timeframe
        start_date (Datetime): start date of historic prices
        end_date (Datetime): end date of historic prices
    """
    columns = {
        'Timestamp': 0,
        'Open': 1,
        'High': 2,
        'Low': 3,
        'Close': 4,
        'Volume': 5
    }

    def __init__(self, tickers, exchange, events_queue, timeframe,
                 start_date=None, end_date=None):
        self.tickers = tickers
        self.exchange = exchange
        self.events_queue = events_queue
        self.timeframe = timeframe
        self.start_date = start_date
        self.end_date = end_date
        self.tickers_data = self.subscribe_tickers()
        self.candles_stream = compose(self.__zip_candles_data_frame)(
            self.__merge_sort_tickers_data())

    def create_candles_data_frame(self, candles):
        return pd.DataFrame.from_records(candles, columns=self.columns.keys())

    @curry
    def add_column_to_data_frame(self, df, col, data):
        return df.assign(
            **{
                col: data
            }
        )

    @curry
    def add_ticker_to_data_frame(self, df, data):
        return self.add_column_to_data_frame(df, 'Ticker', data)

    def subscribe_tickers(self):
        """Get historic data for each ticker in ticker array

        Returns:
            List: DataFrames with ohclv candles with timestamps and ticker
        """
        candles_awaitables = map(self.get_candles_data_frame, self.tickers)
        tickers_data = compose(self.exchange.loop.run_until_complete,
                               asyncio.gather)(*candles_awaitables)

        return compose(dict, zip)(self.tickers, tickers_data)

    async def get_candles_data_frame(self, ticker):
        # Produce add ticker function that accepts data frame parameter
        add_ticker = self.add_ticker_to_data_frame(data=ticker)
        return compose(add_ticker, self.create_candles_data_frame)(
            await self.exchange.get_candles(
                ticker, self.timeframe, self.start_date, self.end_date
            ))

    def __merge_sort_tickers_data(self):
        """
        Sorting dataframes dictionary by timestamp
        """
        return pd.concat(self.tickers_data.values()).sort_values(
            [*self.columns.keys()][0]
        )

    def __zip_candles_data_frame(self, df):
        return compose(zip)(*map(df.get, self.columns.keys()))

    def create_bar_event(self, candle):
        return BarEvent(
            candle[self.columns['Timestamp']],
            candle[self.columns['High']],
            candle[self.columns['Open']],
            candle[self.columns['Low']],
            candle[self.columns['Close']],
            candle[self.columns['Volume']],
            self.timeframe
        )

    async def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        try:
            candle = next(self.candles_stream)
        except StopIteration:
            bar_event = None
        else:
            bar_event = self.create_bar_event(candle)
        finally:
            await self.events_queue.put(bar_event)
            return bar_event
