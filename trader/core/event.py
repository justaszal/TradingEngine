from enum import Enum
from abc import ABC

EventType = Enum('event_types', 'TICK BAR SIGNAL ORDER FILL')
ActionType = Enum('action_types', 'long short')
OrderType = Enum('order_types', 'market limit stop_loss take_profit')


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
        return 'Type: %s, Ticker: %s, Time: %s, Bid: %s, Ask: %s' % (
            str(self.type), str(self.ticker),
            str(self.time), str(self.bid), str(self.ask)
        )

    def __repr__(self):
        return str(self)


class BarEvent(Event):

    def __init__(self, ticker, timestamp, open, high, low, close,
                 volume, timeframe):
        self.type = EventType.BAR
        # self.exchange = exchange
        self.ticker = ticker
        self.timestamp = timestamp

        self.open = open
        self.high = high
        self.low = low
        self.close = close

        self.volume = volume
        self.timeframe = timeframe

    def __str__(self):
        return 'BarEvent: {} {} {} {} {} {} {} {}'.format(
            self.ticker, self.timestamp, self.open, self.high, self.low,
            self.close, self.volume, self.timeframe
        )


class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, timestamp, ticker, action, order_type, price,
                 combined_signals=None):
        """
        Initialises the SignalEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'BTC/USD'.
        action - 'long' or 'short'.
        """
        self.type = EventType.SIGNAL
        self.timestamp = timestamp
        self.ticker = ticker
        self.action = ActionType[action]
        self.order_type = OrderType[order_type]
        self.price = price
        # Take profit, Stop limit
        self.combined_signals = combined_signals

    def __str__(self):
        return ('Timestamp {}, Ticker: {}, Action type: {}, Order type: {},'
                'Price: {}, Combined_signals: {}').format(
            self.timestamp, self.ticker, self.action, self.order_type,
            self.price, self.combined_signals
        )


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a ticker (e.g. ETH/USD), action (long or short)
    and quantity.
    """

    def __init__(self, timestamp, ticker, action, order_type,
                 price, quantity):
        """
        Initialises the OrderEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'ETH/EUR'.
        action - 'long' or 'short'.
        quantity - The quantity of shares to transact.
        """
        self.type = EventType.ORDER
        self.timestamp = timestamp
        self.ticker = ticker
        self.action = ActionType[action]
        self.order_type = OrderType[order_type]
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return 'Order: Timestamp=%s, Ticker=%s, Action=%s, Quantity=%s\
        Price=%s Order=%s' % (
            self.timestamp, self.ticker, self.action, self.quantity,
            self.price, self.order_type
        )


class FillEvent(Event):
    """
    Encapsulates the notion of a filled order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(
        self, timestamp, ticker, action, quantity, price,
        commission, exchange
    ):
        """
        Initialises the FillEvent object.

        timestamp - The timestamp when the order was filled.
        ticker - The ticker symbol, e.g. 'BTC/USD'.
        action(ActionType) - long/short
        quantity - The filled quantity.
        exchange - The exchange where the order was filled.
        price - The price at which the trade was filled.
        commission - The brokerage commission for carrying out the trade.
        """
        self.type = EventType.FILL
        self.timestamp = timestamp
        self.ticker = ticker
        self.action = ActionType[action]
        self.quantity = quantity
        self.exchange = exchange
        self.price = price
        self.commission = commission

        def __str__(self):
            return (
                'Fill event: timestamp: {}, ticker: {}, action: {},'
                'quantity: {}, exchange:{}, price: {}, commission {}'
            ).format(
                self.timestamp, self.ticker, self.action, self.quantity,
                self.exchange, self.price, self.commission
            )
