import pandas as pd
import queue
from functools import reduce
from core.exchange.ccxt_exchange import CCXT
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
        self.tickers_data = self.subscribe_tickers(
            tickers, start_date, end_date)
        self.bar_stream = self.create_bar_stream(self.tickers)

    def create_bar_stream(self, tickers):
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        return pd.DataFrame.from_records(self.tickers, columns=columns)

    def filter_tickers(self, tickers):
        return [*map(lambda arr: arr[0:6], tickers)]

    def subscribe_tickers(self, tickers, start_date, end_date):
        def subscribe(tickers_data, ticker):
            tickers_data[ticker] = self.subscribe_ticker(self, ticker,
                                                         start_date, end_date)
            return tickers_data

        return reduce(
            subscribe
            tickers,
            {}
        )

    def subscribe_ticker(self, tickers, start_date, end_date):
        """
        Subscribe the price handler to a new ticker symbol.
        """
        if ticker not in self.tickers:
            try:
                self._open_ticker_price_csv(ticker)
                dft = self.tickers_data[ticker]
                row0 = dft.iloc[0]

                close = PriceParser.parse(row0["Close"])
                adj_close = PriceParser.parse(row0["Adj Close"])

                ticker_prices = {
                    "close": close,
                    "adj_close": adj_close,
                    "timestamp": dft.index[0]
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                print(
                    "Could not subscribe ticker %s "
                    "as no data CSV found for pricing." % ticker
                )
        else:
            print(
                "Could not subscribe ticker %s "
                "as is already subscribed." % ticker
            )

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        index, row = next(self.bar_stream)
        print("stream_next")
        print(index)
        print(row)
