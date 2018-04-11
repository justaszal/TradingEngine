import ccxt
import core.utils.date_utils as date_utils
import core.utils.filters as filters
from ccxt import (NetworkError,
                  ExchangeError)
from .exchange_errors import (ExchangeNotFoundError,
                              InvalidHistoryTimeframeError,
                              ExchangeRequestError)
from toolz import pipe


class CCXT:

    def __init__(self, name):
        try:
            self.api = getattr(ccxt, name)({
                'enableRateLimit': True
            })
            self.load_markets()
            self.name = name
        except Exception:
            raise ExchangeNotFoundError(name=name)

    def load_markets(self):
        """
        If you forget to load markets the ccxt library will do that
        automatically upon first call to the unified API. It will send
        two HTTP requests, first for markets and then the second one
        for other data, sequentially.
        """
        print('load')
        return self.api.load_markets() if self.api else None

    def get_klines(self, symbol, timeframe, params={}):
        """Gets candlestick history (binance)

        Args:
            symbol (String): uppercase ticker like BTC/USDT - mandatory
            timeframe (String): candle frequency - mandatory
            params (Dict, optional): {
                limit (Int): limit of candles
                startTime (String): timestamp of candlesticks start date
                endTime (String): timestamp of candlesticks end date
            }

        Returns:
            List: candlestick data:
                open date, open, high, low, close, volume, close date,
                quote asset volume, number of trades,
                taker buy base asset volume, taker buy quote asset volume,
                ignore

        Raises:
            AttributeError: publicGetKlines does not exist
            ExchangeRequestError: request to exchange failed
            InvalidHistoryTimeframeError: Timeframe does not exist
        """
        if not getattr(self.api, 'publicGetKlines'):
            raise AttributeError

        if not self.is_timeframe(timeframe):
            raise InvalidHistoryTimeframeError(timeframe=timeframe)

        api_params = {
            **{
                'symbol': symbol,
                'interval': timeframe
            },
            **params
        }

        try:
            candles = self.api.publicGetKlines(api_params)
        except (ExchangeError, NetworkError) as e:
            raise ExchangeRequestError(e)

        return candles

    @staticmethod
    def get_fech_ohlcv_limit(timeframe, start_dt, end_dt=None, limit=None):
        if end_dt:
            timeframes = date_utils.get_data_range_length(start_dt,
                                                          end_dt,
                                                          freq=timeframe)
            limit = (timeframes if
                     limit is None or limit > timeframes else
                     limit)

        return limit

    def get_candles(self, symbol, timeframe, start_dt, end_dt=None, limit=None,
                    params={}):
        if not getattr(self.api, 'fetch_ohlcv'):
            raise AttributeError

        if not self.is_timeframe(timeframe):
            raise InvalidHistoryTimeframeError(timeframe=timeframe)

        limit = self.get_fech_ohlcv_limit(
            timeframe, start_dt, end_dt, limit)

        if limit is not None:
            params['limit'] = limit

        api_params = {
            **{
                'symbol': symbol,
                'timeframe': timeframe,
                'since': date_utils.timestamp_ms_short(start_dt)
            },
            **params
        }
        candles = []

        try:
            while api_params['limit'] > 0:
                fetched_candles = self.api.fetch_ohlcv(**api_params)
                candles += fetched_candles
                candles_count = len(fetched_candles)
                api_params['since'] += date_utils.timeframes_to_seconds(
                    timeframe, candles_count)
                api_params['limit'] -= candles_count
                # print('limit: ', api_params['limit'])
                # print('candles_count: ', candles_count)
                # print('candles to seconds: ', date_utils.timeframes_to_seconds(
                #     timeframe, candles_count))

        except (ExchangeError, NetworkError) as e:
            raise ExchangeRequestError(e)

        return candles

    def is_timeframe(self, t):
        return t in self.api.timeframes

# 1514764800000
# group1 = asyncio.gather(
#     binance.get_candles('BTCUSDT', '1h', 1)
#     # binance.poll()
# )

# r = loop.run_until_complete(group1)
# # await binance.api.close()
