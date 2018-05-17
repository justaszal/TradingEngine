from abc import ABCMeta, abstractmethod
from core.event import OrderType, FillEvent, EventType


class CCXTSimulatedExecutionHandler(object):

    def __init__(self, events_queue, price_handler, orders_registry=None):
        self.events_queue = events_queue
        self.price_handler = price_handler
        self.orders_registry = orders_registry
        self.exchange = self.price_handler.exchange

    def __calculate_comission(self, order_type, quantity, fill_price):
        fee = None
        if order_type == 'market':
            fee = self.exchange.get_fee()['maker']
        elif hasattr(OrderType, order_type):
            fee = self.exchange.get_fee()['taker']

        return (fee * quantity * fill_price) if fee else None

    async def execute_order(self, event):
        """
        Takes an OrderEvent and executes it, producing
        a FillEvent that gets placed onto the events queue.

        Parameters:
        event - Contains an Event object with order information.
        """
        if event.type == EventType.ORDER:
            # Obtain values from the OrderEvent
            timestamp = self.price_handler.get_last_timestamp(event.ticker)
            ticker = event.ticker
            action = event.action.name
            order_type = event.order_type.name
            quantity = event.quantity

            # Obtain the fill price
            if self.price_handler.istick():
                pass
                # bid, ask = self.price_handler.get_best_bid_ask(ticker)
                # if event.action == 'long':
                #     fill_price = ask
                # else:
                #     fill_price = bid
            else:
                fill_price = self.price_handler.get_last_close(ticker)

            commission = self.__calculate_comission(
                order_type, quantity, fill_price)

            # Create the FillEvent and place on the events queue
            fill_event = FillEvent(
                timestamp, ticker, action, quantity, fill_price, commission,
                self.exchange.name
            )
            print('Put Fill event: {}'.format(fill_event.__dict__))
            await self.events_queue.put(fill_event)

            if self.orders_registry is not None:
                self.orders_registry.record_trade(fill_event)
