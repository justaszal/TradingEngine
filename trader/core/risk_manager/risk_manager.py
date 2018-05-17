from abc import ABC, abstractmethod


class RiskManager(ABC):

    @abstractmethod
    def create_order(self, portfolio, signal_event):
        raise NotImplementedError("Should implement refine_orders()")
