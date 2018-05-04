import asyncio
import core.utils.functional as functional
from toolz import curry
from functools import reduce


async def fetch_ohlcv(symbol, timeframe, since=None, limit=1000):
    return reduce(
        lambda data_set, ohlcv: functional.append(
            data_set,
            [1, 1, 1, 1, 1, 1]),
        range(limit if limit < 1000 else 1000), []
    )


async def noop_async(*args):
    return None


def noop(*args):
    return None


class EmptyClass:
    pass
