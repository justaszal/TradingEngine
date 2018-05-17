import numpy as np


class Position:

    def __init__(
        self, timestamp, action, ticker, init_quantity,
        price, commission
    ):
        self.timestamp = timestamp
        self.action = action
        self.ticker = ticker
        self.quantity = init_quantity
        self.price = price
        self.commission = commission
        self.entry = None
        self.exit = None
        self.exit_timestamp = None

        self._calculate_initial_value()

    def _calculate_initial_value(self):
        if self.action == 'long':
            self.entry = self.price * self.quantity - self.commission
            print('Entry, Commission:', self.entry, self.commission)

    def sell_position(self, timestamp, quantity, price, commission):
        self.exit = price * quantity - commission
        self.profit = ((self.exit / self.entry) - 1) * 100
        self.exit_timestamp = timestamp
        print('Exit, Commission:', self.exit, commission)

    def toJSON(self):
        return dict(
            timestamp=np.float64(self.timestamp).item(),
            action=self.action,
            ticker=self.ticker,
            quantity=np.float64(self.quantity).item(),
            price=np.float64(self.price).item(),
            commission=np.float64(self.commission).item(),
            entry=np.float64(self.entry).item(),
            exit=np.float64(self.exit).item(),
            exit_timestamp=np.float64(self.exit_timestamp).item()
        )
