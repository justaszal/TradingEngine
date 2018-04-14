from core.exchange.ccxt_exchange import CCXT
# import core.utils.filters as filters
import core.utils.date_utils as date_utils
# import time
import datetime
import pandas as pd
# import pytz
from functools import reduce
from fn import F, _
import toolz
# from core.price_handler.ccxt_historic_klines\
#     import CCXTHistoricKlinesPriceHandler
import queue
import time
import rx


def function_time(f, *args):
    start = time.time()
    binance.api.fetch_ticker(*args)
    end = time.time()
    print(f.__name__, 'took ', end - start, 'seconds to execute')


tickers = ['BTC/USD']

binance = CCXT('binance')
# function_time(binance.api.fetch_ticker, 'BTC/USD')
start_dt = datetime.datetime(2018, 1, 1)
end_dt = datetime.datetime(2018, 1, 14)

# candles = binance.get_candles('BTC/USDT', '1h', start_dt, end_dt)
events_queue = queue.Queue()

# ccxt_price_handler = CCXTHistoricKlinesPriceHancdler(
# tickers, exchange, events_queue, start_dt, end_dt)
# next_candle = ccxt_price_handler.stream_next()
# print(len(candles))
# print(next_candle)

# d = toolz.assoc({}, 'x', 1)


def push_five_strings(observer):
    i = 0
    while i < 5:
        observer.on_next(1)
        i += 2

    observer.on_completed()


class PrintObserver(rx.Observer):

    def on_next(self, value):
        print("Received {0}".format(value))

    def on_completed(self):
        print("Done!")

    def on_error(self, error):
        print("Error Occurred: {0}".format(error))


# source = rx.Observable.create(push_five_strings)
# source.subscribe(PrintObserver())

# candles = binance.get_candles('BTC/USDT', '1h', start_dt, end_dt)
d = {
    'col1': [1, 2],
    'col2': [1, 3]
}
df = pd.DataFrame(data=d)
print(df.iterrows())
source = rx.Observable.from_(df.iterrows())\
                      .subscribe(
                        on_next=lambda x: print(x[1]['col1'])
                      )
print('Subscribed')
