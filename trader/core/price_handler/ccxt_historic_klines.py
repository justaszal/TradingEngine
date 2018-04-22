import pandas as pd
import queue
import asyncio
from functools import reduce
from toolz import compose, curry
from core.exchange.ccxt_exchange import CCXT
from .base import AbstractPriceHandler


class CCXTHistoricKlinesPriceHandler(AbstractPriceHandler):
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

    def __init__(self, tickers, exchange, events_queue, timeframe,
                 start_date, end_date):
        self.tickers = tickers
        self.exchange = exchange
        self.events_queue = events_queue
        self.timeframe = timeframe
        self.start_date = start_date
        self.end_date = end_date
        self.tickers_data = self.subscribe_tickers()
        # TODO: write create_bar_stream
        # self.bar_stream = self.create_bar_stream()

    def create_candles_stream(self, candles):
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        return pd.DataFrame.from_records(candles, columns=columns)

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

    def filter_tickers(self, tickers):
        return [*map(lambda arr: arr[0:6], tickers)]

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
        add_ticker = self.add_ticker_to_data_frame(data=ticker)

        return compose(add_ticker, self.create_candles_stream)(
            await self.exchange.get_candles(
                ticker, self.timeframe, self.start_date, self.end_date
            ))

    # TODO write stream_next and bar stream iterator
    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        index, row = next(self.bar_stream)
