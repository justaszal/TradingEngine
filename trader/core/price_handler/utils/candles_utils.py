import pandas as pd
from toolz import curry
from core.event import BarEvent

columns = {
    'timestamp': 0,
    'open': 1,
    'high': 2,
    'low': 3,
    'close': 4,
    'volume': 5
}

columns_with_ticker = {
    **columns,
    'ticker': 6
}


@curry
def create_bar_event(candle, timeframe):
    return BarEvent(
        candle[columns_with_ticker['ticker']],
        candle[columns_with_ticker['timestamp']],
        candle[columns_with_ticker['high']],
        candle[columns_with_ticker['open']],
        candle[columns_with_ticker['low']],
        candle[columns_with_ticker['close']],
        candle[columns_with_ticker['volume']],
        timeframe
    )


def create_candles_data_frame(candles):
    return pd.DataFrame.from_records(candles, columns=columns.keys())
