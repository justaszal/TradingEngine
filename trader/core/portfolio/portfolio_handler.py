from core.portfolio.abstract_portfolio_handler import AbstractPortfolioHandler
from core.portfolio.portfolio import Portfolio


class PortfolioHandler(AbstractPortfolioHandler):

    def __init__(self, exchange, capital, base_currency, events_queue,
                 price_handler, risk_manager):
        super().__init__(capital, base_currency, events_queue, price_handler,
                         risk_manager)
        self.portfolio = Portfolio(exchange, self.capital, self.price_handler)

    async def on_signal(self, signal_event):
        """
        This is called by the backtester or live trading architecture
        to form the initial orders from the SignalEvent.

        These orders are sent to the RiskManager to verify,modify or
        eliminate.

        Once received from the RiskManager they are converted into
        full OrderEvent objects and sent back to the events queue.

        Args:
            signal_event (SignalEvent)
        """
        # print('Got signal: {}'.format(signal_event))
        order_event = self.risk_manager.create_order(
            self.portfolio, signal_event)
        print('Putting order event', order_event)
        await self.events_queue.put(order_event)

    async def on_fill(self, fill_event):
        """
        This is called by the backtester or live trading architecture
        to take a FillEvent and update the Portfolio object with new
        or modified Positions.

        Upon receipt of a FillEvent, the PortfolioHandler converts
        the event into a transaction that gets stored in the Portfolio
        object. This ensures that the broker and the local portfolio
        are "in sync".
        """
        timestamp = fill_event.timestamp
        action = fill_event.action
        ticker = fill_event.ticker
        quantity = fill_event.quantity
        price = fill_event.price
        commission = fill_event.commission
        # Create or sell the position from the fill info
        self.portfolio.process_position(
            timestamp, action, ticker, quantity, price, commission
        )

    def get_portfolio_report(self):
        return {
            'closed_positions': self.portfolio.closed_positions,
            'initial_capital': self.portfolio.initial_capital,
            'capital': self.portfolio.capital,
            'equity': self.portfolio.equity
        }
