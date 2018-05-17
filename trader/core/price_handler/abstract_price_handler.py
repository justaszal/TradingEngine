from abc import ABC, abstractmethod
from toolz import curry, compose
import pandas as pd
import core.utils.date_utils as date_utils
import core.utils.pandas_utils as pandas_utils
import core.price_handler.utils.candles_utils as candles_utils


class AbstractPriceHandler(ABC):

    @abstractmethod
    def stream_next(self):
        raise NotImplementedError('Should implement stream_next')

    def unsubscribe_ticker(self, ticker_data, tickers, ticker):
        """
        Unsubscribes the price handler from a current ticker symbol.
        """
        try:
            self.tickers.remove(ticker)
            if getattr(self, tickers_data):
                delattr(self.tickers_data, ticker)
        except KeyError:
            print(
                'Could not unsubscribe ticker %s '
                'as it was never subscribed.' % ticker
            )


class LivePriceHandler:

    def get_last_ticker_data(self, ticker):
        """
        Returns the last bar updated.
        """
        return self.get_latest_tickers_data(ticker)

    def get_latest_tickers_data(self, ticker, n=1):
        """
        Returns the last N bars updated.
        """
        try:
            return (self.tickers_data[ticker].iloc[-n]
                    if ticker in self.tickers_data
                    else None)
        except IndexError:
            return None


class HistoricPriceHandler:

    def get_last_ticker_data(self, ticker):
        """
        Returns the last bar updated.
        """
        try:
            index = self.tickers_data_index[ticker]
            return (self.tickers_data[ticker].iloc[index]
                    if index != -1
                    else None)
        except IndexError:
            return None

    def get_latest_tickers_data(self, ticker, n=1):
        """
        Returns the last N bars updated.
        """
        try:
            index = self.tickers_data_index[ticker]
            return (self.tickers_data[ticker].iloc[index - n:index]
                    if index != -1
                    else None)
        except IndexError:
            return None


class AbstractBarPriceHandler(AbstractPriceHandler):
    """
    AbstractBarPriceHandler is a base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) AbstractBarPriceHandler object is to output a set
    of TickEvents or BarEvents for each financial instrument and place
    them into an event queue.

    This will replicate how a live strategy would function as current
    tick/bar data would be streamed via a brokerage. Thus a historic and live
    system will be treated identically by the rest of the system.
    """

    def istick(self):
        return False

    def isbar(self):
        return True

    @curry
    def _get_candles_data_frame(self, ticker, candles):
        add_to_data_frame = pandas_utils.add_ticker_to_data_frame(data=ticker)
        return compose(add_to_data_frame,
                       candles_utils.create_candles_data_frame)(candles)

    def get_last_close(self, ticker):
        candle = self.get_last_ticker_data(ticker)
        return None if candle is None else candle['close']

    def get_first_tickers_data(self, ticker, n=0):
        try:
            return (self.tickers_data[ticker].iloc[n]
                    if ticker in self.tickers
                    else None)
        except IndexError:
            return None

    def get_first_timestamp(self, ticker):
        candle = self.get_first_tickers_data(self.tickers[0])
        return None if candle is None else candle['timestamp']

    def get_last_timestamp(self, ticker):
        candle = self.get_last_ticker_data(ticker)
        return None if candle is None else candle['timestamp']
