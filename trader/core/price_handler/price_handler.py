from abc import ABC, abstractmethod


class PriceHandler(ABC):
    """
    PriceHandler is a base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) PriceHandler object is to output a set of
    TickEvents or BarEvents for each financial instrument and place
    them into an event queue.

    This will replicate how a live strategy would function as current
    tick/bar data would be streamed via a brokerage. Thus a historic and live
    system will be treated identically by the rest of the system.
    """

    def __init__(self, tickers, exchange, events_queue, timeframe='1m'):
        self.tickers = tickers
        self.exchange = exchange
        self.events_queue = events_queue
        self.timeframe = timeframe

    @abstractmethod
    def stream_next(self):
        raise NotImplementedError("Should implement stream_next")

    def unsubscribe_ticker(self, ticker):
        """
        Unsubscribes the price handler from a current ticker symbol.
        """
        try:
            self.tickers.remove(ticker)
            if getattr(self, tickers_data):
                delattr(self.tickers_data, ticker)
        except KeyError:
            print(
                "Could not unsubscribe ticker %s "
                "as it was never subscribed." % ticker
            )
