import pandas as pd
from toolz import curry
from core.event import BarEvent

columns = {
    'Timestamp': 0,
    'Open': 1,
    'High': 2,
    'Low': 3,
    'Close': 4,
    'Volume': 5
}

columns_with_ticker = {
    **columns,
    'Ticker': 6
}


@curry
def create_bar_event(candle, timeframe):
    return BarEvent(
        candle[columns_with_ticker['Ticker']],
        candle[columns_with_ticker['Timestamp']],
        candle[columns_with_ticker['High']],
        candle[columns_with_ticker['Open']],
        candle[columns_with_ticker['Low']],
        candle[columns_with_ticker['Close']],
        candle[columns_with_ticker['Volume']],
        timeframe
    )


def create_candles_data_frame(candles):
    return pd.DataFrame.from_records(candles, columns=columns.keys())
