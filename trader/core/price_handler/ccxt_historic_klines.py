import pandas as pd
import queue
import core.exchange.ccxt_exchange
from .base import AbstractPriceHandler


class CCXTHistoricKlinesPriceHandler(AbstractPriceHandler):

    """
    CCXTHistoricKlinesPriceHandler is designed to fetch historic price then
    produce a dataframe of cryptocurrency exchange Open-High-Low-Close-Volume
    (OHLCV) data for each requested financial instrument and stream those to
    the provided events queue as bar events.

    Attributes:
        tickers (List): ticker format => 'BTC_USDT'
        exchange (String): cryptocurrency exhange
        events_queue (Queue): events queue consumed by trading engine
        start_date (Datetime): start date of historic prices
        end_date (Datetime): end date of historic prices
    """

    def __init__(self, tickers, exchange, events_queue, start_date, end_date):
        self.tickers = tickers
        self.exchange = exchange
        self.events_queue = events_queue
        self.start_date = start_date
        self.end_date = end_date
        self.stream_next()

    def create_bar_stream(self, tickers):
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        return pd.DataFrame.from_records(self.tickers, columns=columns)

    def filter_tickers(self, tickers):
        return [*map(lambda arr: arr[0:6], tickers)]

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        index, row = next(self.bar_stream)
        print(index)
        print(row)


# binance = CCXT('binance')
# tickers = binance.get_tickers('BTCUSDT', '1h', {
#     'limit': 1,
#     'startTime': date_utils.timestamp_ms_short_utc((2017, 11, 1)),
#     'endTime': date_utils.timestamp_ms_short_utc((2018, 1, 1))
# })
