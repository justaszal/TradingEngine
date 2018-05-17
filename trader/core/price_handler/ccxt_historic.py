import pandas as pd
import asyncio
import core.price_handler.utils.candles_utils as candles_utils
import core.utils.pandas_utils as pandas_utils
from toolz import compose
from core.price_handler.abstract_price_handler import (AbstractBarPriceHandler,
                                                       HistoricPriceHandler)


class CCXTHistoricPriceHandler(AbstractBarPriceHandler, HistoricPriceHandler):
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
    @classmethod
    async def create(cls, tickers, exchange, events_queue, timeframe='1m',
                     start_date=None, end_date=None):
        self = CCXTHistoricPriceHandler()
        self.tickers = tickers
        self.exchange = exchange
        self.events_queue = events_queue
        self.timeframe = timeframe
        self.start_date = start_date
        self.end_date = end_date
        # Dict of DataFrames
        self.tickers_data = await self.__subscribe_tickers()
        self.candles_stream = compose(self.__zip_candles_data_frame)(
            self.__sort_tickers_data())
        self.tickers_data_index = dict(
            zip(self.tickers, [-1] * len(self.tickers))
        )

        return self

    async def get_candles(self, ticker):
        return await self.exchange.get_candles(
            ticker,
            timeframe=self.timeframe,
            start_date=self.start_date,
            end_date=self.end_date
        )

    async def __subscribe_tickers(self):
        """Get historic data for each ticker in ticker array

        Returns:
            Dict: DataFrames with ohclv candles with timestamps and ticker
        """
        async def get_candles_data_frame(ticker):
            candles = await self.get_candles(ticker)
            return self._get_candles_data_frame(ticker, candles)

        # candles_awaitables = map(get_candles_data_frame, self.tickers)

        tickers_data = []
        for index, ticker in enumerate(self.tickers):
            df = await get_candles_data_frame(ticker)
            tickers_data.append(df)

        return compose(dict, zip)(self.tickers, tickers_data)

    def __sort_tickers_data(self):
        """
        Sorting dataframes dictionary by timestamp
        """
        return pd.concat(self.tickers_data.values()).sort_values(
            [*candles_utils.columns.keys()][0]
        )

    def __zip_candles_data_frame(self, df):
        return compose(zip)(
            *map(df.get, candles_utils.columns_with_ticker.keys())
        )

    async def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        try:
            candle = next(self.candles_stream)
            bar_event = candles_utils.create_bar_event(candle, self.timeframe)
            print('bar_event: ', type(bar_event), bar_event)
            self.tickers_data_index[bar_event.ticker] += 1
        except StopIteration:
            bar_event = None
        finally:
            await self.events_queue.put(bar_event)
            return True if bar_event else None
