from abc import ABC, abstractmethod


class AbstractPortfolioHandler(ABC):
    """
    The PortfolioHandler is designed to interact with the
    backtesting or live trading overall event-driven
    architecture. It exposes two methods, on_signal and
    on_fill, which handle how SignalEvent and FillEvent
    objects are dealt with.
    """

    def __init__(self, capital, base_currency, events_queue, price_handler,
                 risk_manager):
        """
        Args:
            capital (Float): Money amount used for trading.
            base_currency (String): Name of currency used for trading.
            events_queue (Queue): Order events are going to be put inside event
                loop.
            price_handler (AbstractPriceHandler): Used by Portfolio to get
                latest price.
            risk_manager (RiskManager): Set Order amount to remain in line with
                risk parameters.
            portfolio (Portfolio): Stores the actual Position objects.
        """
        self.capital = capital
        self.base_currency = base_currency
        self.events_queue = events_queue
        self.price_handler = price_handler
        self.risk_manager = risk_manager

    @abstractmethod
    def on_signal(self):
        raise NotImplementedError("Should implement on_signal")

    @abstractmethod
    def on_fill(self):
        raise NotImplementedError("Should implement on_fill")
