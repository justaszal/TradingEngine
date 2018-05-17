from abc import ABC, abstractmethod


class Strategy(ABC):
    """
    Strategy is an abstract base class providing an interface for
    all subsequent (inherited) strategy handling objects.

    The goal of a (derived) Strategy object is to generate Signal
    objects for particular symbols based on the inputs of ticks
    generated from a AbstractPriceHandler (derived) object.

    This is designed to work both with historic and live data as
    the Strategy object is agnostic to data location.
    """

    @abstractmethod
    def calculate_signal(self, event):
        raise NotImplementedError("Should implement calculate_signal")
