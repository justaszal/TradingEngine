class TradingSession:
    """
    Enscapsulates the settings and components for
    carrying out either a backtest or live trading session.
    """

    def __init__(self, events_queue, exchange, tickers, heartbeat=1,
                 start_date, end_date, session_type="backtest"):
        """
        Args:
            events_queue: events to process inside event loop
                event types: TICK, BAR
            exchange: exchange object
            tickers: list of tickers
            start_date: datetime object, start of loop
            end_date: datetime object, end of loop
            heartbeat: delay in seconds between loop iterations (default: {1})
            session_type: backtest/live (default: {"backtest"})
        """
        self.events_queue = events_queue
        self.exchange = exchange
        self.tickers = tickers
        self.heartbeat = heartbeat
        self.start_date = start_date
        self.end_date = end_date
        self.session_type = session_type
