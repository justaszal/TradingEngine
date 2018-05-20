from core.price_handler.ccxt_historic import CCXTHistoricPriceHandler
from core.price_handler.ccxt_live import CCXTLivePriceHandler
from core.price_handler.abstract_price_handler import AbstractBarPriceHandler
from core.errors import (TradingSessionTypeError,
                         PriceHandlerNotFoundError)
from core.risk_manager.portfolio_percentage_risk_manager\
    import PortfolioPercentageRiskManager
from core.event import EventType
from core.portfolio.portfolio_handler import PortfolioHandler
from toolz import compose
from core.execution_handler.ccxt_simulated import CCXTSimulatedExecutionHandler
import asyncio
import core.utils.date_utils as date_utils
import core.configuration as configuration
import datetime


class TradingSession:
    """
    Enscapsulates the settings and components for
    carrying out either a backtest or live trading session.
    """
    @classmethod
    async def create(cls, exchange, tickers, events_queue, strategy,
                     capital, base_currency='USD', start_date=None,
                     end_date=None, timeframe="1h", session_type="backtest",
                     price_handler=None, risk_manager=None,
                     portfolio_handler=None, execution_handler=None,
                     orders_registry=None):
        self = TradingSession()
        self.exchange = exchange
        self.tickers = tickers
        self.events_queue = events_queue
        self.strategy = strategy
        self.capital = capital
        self.base_currency = base_currency
        self.start_date = start_date
        self.session_start_date = datetime.datetime.now()
        self.end_date = end_date
        self.timeframe = timeframe
        self.session_type = session_type
        self.price_handler = price_handler
        self.risk_manager = risk_manager
        self.portfolio_handler = portfolio_handler
        self.execution_handler = execution_handler
        self.orders_registry = orders_registry
        await self.__config_session()

        return self

    async def __config_session(self):
        """
        Session configuration
        """
        self.heartbeat = (
            date_utils.timeframes_to_seconds(self.timeframe)
            if self.session_type == 'live'
            else None
        )
        await self.__set_price_handler(self.price_handler)
        print('__set_price_handler: ', self.price_handler)

        if self.risk_manager is None:
            self.risk_manager = PortfolioPercentageRiskManager(2)

        if self.portfolio_handler is None:
            self.portfolio_handler = PortfolioHandler(
                self.exchange, self.capital, self.base_currency,
                self.events_queue, self.price_handler, self.risk_manager
            )

        if self.execution_handler is None:
            self.execution_handler = CCXTSimulatedExecutionHandler(
                self.events_queue, self.price_handler, self.orders_registry
            )

    async def __set_price_handler(self, price_handler):
        price_handler_args = (
            self.tickers, self.exchange, self.events_queue, self.timeframe,
            self.start_date, self.end_date
        ) if self.session_type == 'backtest' else (
            self.tickers, self.exchange, self.events_queue, self.timeframe,
            self.end_date
        ) if self.session_type == 'live' else None

        if price_handler_args is None:
            raise TradingSessionTypeError(session_type=self.session_type)

        if self.price_handler is None:
            if self.session_type == 'backtest':
                print('price_handler_args: ', price_handler_args)
                self.price_handler = await CCXTHistoricPriceHandler.create(
                    *price_handler_args)
            elif self.session_type == 'live':
                self.price_handler = CCXTLivePriceHandler(*price_handler_args)
        elif isinstance(self.price_handler, str):
            price_handler_class = configuration.load_price_handler_class(
                self.price_handler, self.session_type)
            if hasattr(price_handler_class, 'create'):
                self.price_handler = await price_handler_class.create(
                    *price_handler_args)
            else:
                self.price_handler = price_handler_class(*price_handler_args)
        else:
            raise PriceHandlerNotFoundError(
                price_handler=self.price_handler)

    async def __stream_events(self):
        while True:
            event = await self.price_handler.stream_next()
            print('Stream bar event: {}'.format(event))
            """
            Price handler returns None when iterator is empty in backtest
            mode
            """
            if event is None:
                print('stream events break')
                break
            await asyncio.sleep(self.heartbeat or 0)

    async def __process_events(self, event_processor=None):
        while True:
            try:
                event = self.events_queue.get_nowait()
                print('Got bar event: {}'.format(event))
            except asyncio.QueueEmpty:
                await asyncio.sleep(1 if self.heartbeat else 0)
            else:
                if event is None:
                    print('process events break')
                    break
                elif (
                    event.type == EventType.TICK or
                    event.type == EventType.BAR
                ):
                    await self.strategy.calculate_signal(event)
                    if event_processor:
                        event_processor(event)
                    """
                    Updates the value of all positions that are currently open.
                    """
                    # self.portfolio_handler.portfolio.update_portfolio()
                elif event.type == EventType.SIGNAL:
                    await self.portfolio_handler.on_signal(event)
                elif event.type == EventType.ORDER:
                    await self.execution_handler.execute_order(event)
                elif event.type == EventType.FILL:
                    await self.portfolio_handler.on_fill(event)
                else:
                    raise NotImplemented(
                        "Unsupported event.type '%s'" % event.type)

    async def run_session(self, event_processor=None):
        await asyncio.gather(self.__stream_events(),
                             self.__process_events(event_processor))

        print("Run session finished")
        # TODO move to a function
        portfolio_report = self.portfolio_handler.get_portfolio_report()

        # Set session start and end dates
        if self.session_type == 'live':
            portfolio_report['start_date'] = date_utils.timestamp_ms_short(
                self.session_start_date)
        elif self.start_date:
            portfolio_report['start_date'] = date_utils.timestamp_ms_short(
                self.start_date)
        else:
            timestamp = self.price_handler.get_first_timestamp(self.tickers[0])
            if timestamp:
                portfolio_report['start_date'] = timestamp

        if self.end_date:
            portfolio_report['end_date'] = date_utils.timestamp_ms_short(
                self.end_date)
        else:
            timestamp = self.price_handler.get_last_timestamp(self.tickers[0])
            if timestamp:
                portfolio_report['end_date'] = timestamp

        tickers_data = self.price_handler.tickers_data

        # for ticker, data in tickers_data.items():
        #     tickers_data[ticker] = data.to_json()

        portfolio_report['tickers_data'] = tickers_data
        return portfolio_report
