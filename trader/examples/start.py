from core.exchange.ccxt_exchange import CCXT
# import core.utils.filters as filters
import core.utils.date_utils as date_utils
# import time
import datetime
import pandas as pd
# import pytz
from functools import reduce
from fn import F, _
from toolz import curry, pipe
# from core.price_handler.ccxt_historic_klines \
# import CCXTHistoricKlinesPriceHandler

tickers = ['BTC/USDT']
binance = CCXT('binance')

dt_start = datetime.datetime(2018, 1, 1)
dt_end = datetime.datetime(2018, 1, 14)
# TODO: Limit for binance is 500 for one request. Make a loop inside
# get_candles to fetch all data in a given timeframe
# candles = binance.get_candles('BTC/USDT', '1h', dt_start, dt_en)
# print(len(candles))
