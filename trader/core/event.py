from enum import Enum
from abc import ABC

EventType = Enum('event_types', 'TICK BAR SIGNAL ORDER FILL')
SignalType = Enum('signal_types', 'long short')


class Event(ABC):
    _type = None

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value


class TickEvent(Event):
    """
    Handles the event of receiving a new market update tick,
    which is defined as a ticker symbol and associated best
    bid and ask from the top of the order book.
    """

    def __init__(self, ticker, time, bid, ask):
        """
        Initialises the TickEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'GOOG'.
        time - The timestamp of the tick
        bid - The best bid price at the time of the tick.
        ask - The best ask price at the time of the tick.
        """
        self.type = EventType.TICK
        self.ticker = ticker
        self.time = time
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return "Type: %s, Ticker: %s, Time: %s, Bid: %s, Ask: %s" % (
            str(self.type), str(self.ticker),
            str(self.time), str(self.bid), str(self.ask)
        )

    def __repr__(self):
        return str(self)


class BarEvent(Event):

    def __init__(self, ticker, timestamp, open, high, low, close, volume,
                 timeframe):
        self.type = EventType.BAR
        self.ticker = ticker
        self.timestamp = timestamp

        self.open = open
        self.high = high
        self.low = low
        self.close = close

        self.volume = volume
        self.timeframe = timeframe

    def __str__(self):
        return "BarEvent: [{} {} {} {} {} {} {} {}]".format(
            self.ticker, self.timestamp, self.open, self.high, self.low,
            self.close, self.volume, self.timeframe
        )


class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, ticker, action):
        """
        Initialises the SignalEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'BTC/USD'.
        action - 'long' or 'short'.
        """
        self.type = EventType.SIGNAL
        self.ticker = ticker
        self.action = SignalType[action]


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a ticker (e.g. ETH/USD), action (long or short)
    and quantity.
    """

    def __init__(self, ticker, action, quantity):
        """
        Initialises the OrderEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'ETH/EUR'.
        action - 'long' or 'short'.
        quantity - The quantity of shares to transact.
        """
        self.type = EventType.ORDER
        self.ticker = ticker
        self.action = action
        self.quantity = quantity

    def print_order(self):
        """
        Outputs the values within the OrderEvent.
        """
        print(
            "Order: Ticker=%s, Action=%s, Quantity=%s" % (
                self.ticker, self.action, self.quantity
            )
        )
