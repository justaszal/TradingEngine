import ccxt.async as ccxt
import asyncio
import core.utils.date_utils as date_utils
import core.utils.filters as filters
from .exchange import ExchangeAsync
from ccxt import (NetworkError,
                  ExchangeError)
from .exchange_errors import (ExchangeNotFoundError,
                              InvalidHistoryTimeframeError,
                              InvalidTickerError,
                              ExchangeRequestError)
from toolz import pipe, compose, first


class CCXT(ExchangeAsync):

    def __init__(self, name):
        try:
            self.api = getattr(ccxt, name)({
                'enableRateLimit': True
            })
            self.markets = compose(
                self.loop.run_until_complete
            )(self.load_markets())
            self.name = name
        except Exception:
            raise ExchangeNotFoundError(exhange_name=name)

    async def load_markets(self):
        """
        If you forget to load markets the ccxt library will do that
        automatically upon first call to the unified API. It will send
        two HTTP requests, first for markets and then the second one
        for other data, sequentially.
        """
        return await self.api.load_markets()

    def close(self):
        compose(self.loop.run_until_complete)(self.api.close())

    def get_klines(self, ticker, timeframe, params={}):
        """Gets candlestick history (binance)

        Args:
            ticker (String): uppercase ticker like BTC/USDT - mandatory
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
                'ticker': ticker,
                'interval': timeframe
            },
            **params
        }

        try:
            candles = self.api.publicGetKlines(api_params)
        except (ExchangeError, NetworkError) as e:
            raise ExchangeRequestError(e)

        return candles

    def get_fech_ohlcv_limit(self, timeframe, start_dt=None, end_dt=None,
                             limit=None):
        if (start_dt and end_dt):
            timeframes = date_utils.get_data_range_length(start_dt,
                                                          end_dt,
                                                          freq=timeframe)
            limit = (timeframes if
                     limit is None or limit > timeframes else
                     limit)

        return limit

    def get_since_date(self, timeframe, start_dt=None, end_dt=None,
                       limit=None):
        since = None

        if (start_dt is None and end_dt and limit):
            limit_seconds = date_utils.timeframes_to_seconds(timeframe, limit)
            since = date_utils.timestamp_ms_short(end_dt) - limit_seconds
        elif (start_dt):
            since = date_utils.timestamp_ms_short(start_dt)

        return since

    async def fetch_ticker(self, ticker):
        return await self.api.fetch_ticker(ticker)

    async def get_candles(self, ticker, timeframe='1m', start_dt=None,
                          end_dt=None, limit=None, params={}):
        self.verify_api_attribute('fetch_ohlcv')
        self.verify_ticker(ticker)
        self.verify_timeframe(timeframe)

        params['since'] = self.get_since_date(timeframe, start_dt, end_dt,
                                              limit)
        params['limit'] = self.get_fech_ohlcv_limit(timeframe, start_dt,
                                                    end_dt, limit)
        api_params = {
            **{
                'symbol': ticker,
                'timeframe': timeframe,
            },
            **filters.get_defined_dict_values(params)
        }

        candles = []

        try:
            if 'limit' in api_params and api_params['limit'] is not None:
                while api_params['limit'] > 0:
                    fetched_candles = await self.api.fetch_ohlcv(**api_params)
                    candles += fetched_candles
                    candles_count = len(fetched_candles)
                    api_params['since'] = first(fetched_candles)[0] + \
                        date_utils.timeframes_to_seconds(
                            timeframe, candles_count
                    )
                    api_params['limit'] -= candles_count
            else:
                fetched_candles = await self.api.fetch_ohlcv(**api_params)
                candles += fetched_candles

        except (ExchangeError, NetworkError) as e:
            raise ExchangeRequestError(e)

        return candles

    def verify_ticker(self, ticker):
        if not self.is_ticker(ticker):
            raise InvalidTickerError(exhange_name=self.name, ticker=ticker)

    def verify_api_attribute(self, attribute):
        if not hasattr(self.api, attribute):
            raise AttributeError

    def verify_timeframe(self, timeframe):
        if not self.is_timeframe(timeframe):
            raise InvalidHistoryTimeframeError(timeframe=timeframe)

    def is_ticker(self, ticker):
        return ticker in self.markets

    def is_timeframe(self, timeframe):
        return timeframe in self.api.timeframes
