from core.portfolio.position import Position


class Portfolio:
    """
    On creation, the Portfolio object contains no
    positions and all values are "reset" to the initial
    cash, with no PnL - realised or unrealised.

    Note that realised_pnl is the running tally pnl from closed
    positions (closed_pnl), as well as realised_pnl
    from currently open positions.
    """

    def __init__(self, exchange, capital, price_handler):
        self.exchange = exchange
        self.initial_capital = capital
        self.capital = capital
        self.equity = 0
        self.positions = {}
        self.closed_positions = []
        self.price_handler = price_handler

    def update_portfolio(self):
        self.equity = 0
        """
        Updates equity
        """
        for ticker in self.positions:
            position = self.positions[ticker]
            close_price = self.price_handler.get_last_close(ticker)
            self.equity += (
                close_price * position.quantity - position.commission
            )

    def __add_position(self, timestamp, action, ticker, quantity, price,
                       commission):
        """
        Adds a new Position object to the Portfolio.
        """
        if ticker not in self.positions:
            position = Position(
                timestamp, action, ticker, quantity, price, commission
            )
            self.positions[ticker] = position
        else:
            print(
                "Ticker %s is already in the positions list. "
                "Could not add a new position." % ticker
            )

    def __modify_position(self, timestamp, action, ticker, quantity, price,
                          commission):
        if ticker in self.positions:
            self.positions[ticker].sell_position(
                timestamp, quantity, price, commission
            )
            closed = self.positions.pop(ticker)
            self.closed_positions.append(closed)
        else:
            print(
                "Ticker %s not in the current position list."
                "Could not modify a current position." % ticker
            )

    def process_position(self, timestamp, action, ticker, quantity, price,
                         commission):
        """
        Handles any new position or modification to
        a current position, by calling the respective
        _add_position and _modify_position methods.

        Hence, this single method will be called by the
        PortfolioHandler to update the Portfolio itself.
        """
        action = action.name
        if action == 'long':
            self.capital -= ((quantity * price) + commission)
        elif action == 'short':
            self.capital += ((quantity * price) - commission)

        if ticker not in self.positions:
            self.__add_position(
                timestamp, action, ticker, quantity,
                price, commission
            )
        else:
            self.__modify_position(
                timestamp, action, ticker, quantity,
                price, commission
            )
        self.update_portfolio()
        print('Processed position: {}'.format(ticker))
        print('portoflio capital: {}'.format(self.capital))
        print('equity: {}'.format(self.equity))
        print('closed_positions: {}'.format(self.closed_positions))
