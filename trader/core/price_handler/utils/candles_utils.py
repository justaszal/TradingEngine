import pandas as pd
from core.event import BarEvent

columns = {
    'Timestamp': 0,
    'Open': 1,
    'High': 2,
    'Low': 3,
    'Close': 4,
    'Volume': 5
}


def create_bar_event(candle, timeframe):
    return BarEvent(
        candle[columns['Timestamp']],
        candle[columns['High']],
        candle[columns['Open']],
        candle[columns['Low']],
        candle[columns['Close']],
        candle[columns['Volume']],
        timeframe
    )


def create_candles_data_frame(candles):
    return pd.DataFrame.from_records(candles,
                                     columns=columns.keys())
