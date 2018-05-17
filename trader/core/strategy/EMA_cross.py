import core.utils.functional as functional
import numpy as np
import core.utils.numpy_utils as numpy_utils
import talib
from core.event import (SignalEvent, EventType)
from collections import deque
from .strategy import Strategy
from functools import reduce


class EMACrossStrategy(Strategy):
    """
    Requires:
        tickers - Array of tickers used to calculate signals
        events_queue - A handle to the system events queue
        short_window - Lookback period for short moving average
        long_window - Lookback period for long moving average
    """

    def __init__(self, tickers, events_queue, short_window=20, long_window=50):
        self.tickers = tickers
        self.events_queue = events_queue
        self.short_window = short_window
        self.long_window = long_window
        """
        Keeps ticker information

        ticker_storage (Dict): {
            bars (ndarray): Storage of latest closed price information
                            Size=long_window
            index (Int): Index of bars array
            is_bought (Boolean): Indicates whether system has opened a position
        }
        """
        self.tickers_storage = self.__init_ticker_storage()

    def __init_ticker_storage(self):
        return reduce(lambda storage, ticker: functional.set_attribute(
            storage, ticker, {
                'bars': np.ndarray((self.long_window,), dtype=np.float),
                'index': 0,
                'is_bought': False
            }
        ), self.tickers, {})

    async def __get_signal(self, ticker, timestamp, ticker_storage):
        # Calculate the exponential moving averages
        bars = ticker_storage['bars']
        window_diff = self.long_window - self.short_window
        short_ema = talib.EMA(
            bars[window_diff:], timeperiod=self.short_window
        )[-1]
        long_ema = talib.EMA(bars, timeperiod=self.long_window)[-1]
        # print('short EMA {}'.format(short_ema))
        # print('long EMA {}'.format(long_ema))
        # Trading signals based on moving average cross
        if short_ema > long_ema and not ticker_storage['is_bought']:
            print("LONG %s: %s, %s" % (ticker, timestamp, bars[-1]))
            signal = SignalEvent(timestamp, ticker, "long", "limit", bars[-1])
            await self.events_queue.put(signal)
            ticker_storage['is_bought'] = True
        elif short_ema < long_ema and ticker_storage['is_bought']:
            print("SHORT %s: %s, %s" % (ticker, timestamp, bars[-1]))
            signal = SignalEvent(
                timestamp, ticker, "short", "limit", bars[-1])
            await self.events_queue.put(signal)
            ticker_storage['is_bought'] = False

    async def calculate_signal(self, event):
        if (
            event.type == EventType.BAR and
            event.ticker in self.tickers_storage
        ):
            ticker_storage = self.tickers_storage[event.ticker]
            index = ticker_storage['index']

            # Firstly fill an array of size long window
            if ticker_storage['index'] < self.long_window:
                ticker_storage['bars'][index] = event.close
                ticker_storage['index'] += 1

                if ticker_storage['index'] == self.long_window:
                    await self.__get_signal(
                        event.ticker, event.timestamp, ticker_storage)
            # Array is full, so remove oldest value, add new and get signal
            else:
                # Shift array to left
                numpy_utils.shift(ticker_storage['bars'], -1)
                ticker_storage['bars'][
                    ticker_storage['index'] - 1] = event.close
                await self.__get_signal(
                    event.ticker, event.timestamp, ticker_storage)
