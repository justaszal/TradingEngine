import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict


class Exchange(ABC):

    @abstractmethod
    def get_candles(self) -> List:
        raise NotImplementedError("Should implement get_candles")

    @abstractmethod
    def fetch_ticker(self) -> Dict:
        raise NotImplementedError("Should implement fetch_ticker")


class ExchangeAsync(Exchange):
    __loop = asyncio.get_event_loop()

    @property
    def loop(self):
        return ExchangeAsync.__loop
