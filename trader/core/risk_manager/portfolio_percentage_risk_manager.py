from core.risk_manager.risk_manager import RiskManager
from core.event import OrderEvent


class PortfolioPercentageRiskManager(RiskManager):

    """
    Adjusts the order size to not risk more that certain % of portfolio
    """

    def __init__(self, risk_pct):
        self.risk_pct = risk_pct / 100 if risk_pct <= 100 else 1

    def create_order(self, portfolio, signal_event):
        amount = portfolio.capital * self.risk_pct

        if (signal_event.action.name == 'long'):
            order_event = OrderEvent(
                signal_event.timestamp,
                signal_event.ticker,
                signal_event.action.name,
                signal_event.order_type.name,
                signal_event.price,
                amount / signal_event.price
            )
        else:
            order_event = OrderEvent(
                signal_event.timestamp,
                signal_event.ticker,
                signal_event.action.name,
                signal_event.order_type.name,
                signal_event.price,
                portfolio.positions[signal_event.ticker].quantity
            )

        return order_event
