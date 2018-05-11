import pandas as pd
import asyncio
import core.price_handler.utils.candles_utils as candles_utils
import core.utils.pandas_utils as pandas_utils
from toolz import compose
from .price_handler import PriceHandler


class CCXTHistoricPriceHandler(PriceHandler):
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

    def __init__(self, tickers, exchange, events_queue, timeframe='1m',
                 start_date=None, end_date=None):
        super().__init__(tickers, exchange, events_queue, timeframe)
        self.start_date = start_date
        self.end_date = end_date
        self.tickers_data = self.__subscribe_tickers()
        self.candles_stream = compose(self.__zip_candles_data_frame)(
            self.__sort_tickers_data())

    def __subscribe_tickers(self):
        """Get historic data for each ticker in ticker array

        Returns:
            List: DataFrames with ohclv candles with timestamps and ticker
        """
        candles_awaitables = map(self.__get_candles_data_frame, self.tickers)
        tickers_data = compose(self.exchange.loop.run_until_complete,
                               asyncio.gather)(*candles_awaitables)

        return compose(dict, zip)(self.tickers, tickers_data)

    async def __get_candles_data_frame(self, ticker):
        # Produce add ticker function that accepts data frame parameter
        add_ticker = pandas_utils.add_ticker_to_data_frame(data=ticker)
        return compose(add_ticker, candles_utils.create_candles_data_frame)(
            await self.exchange.get_candles(
                ticker, self.timeframe, self.start_date, self.end_date
            ))

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
        except StopIteration:
            bar_event = None
        else:
            bar_event = candles_utils.create_bar_event(candle, self.timeframe)
        finally:
            await self.events_queue.put(bar_event)
            return True if bar_event else None
