import pandas as pd
from toolz import curry


@curry
def add_column_to_data_frame(df, col, data):
    return df.assign(
        **{
            col: data
        }
    )


@curry
def add_ticker_to_data_frame(df, data):
    return add_column_to_data_frame(df, 'ticker', data)
