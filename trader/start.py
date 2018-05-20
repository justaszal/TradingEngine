# import core.server as server
from core.exchange.ccxt_exchange import CCXT
import core.utils.filters as filters
import core.utils.date_utils as date_utils
import datetime
import pandas as pd
import pytz
from functools import reduce
from fn import F, _
from toolz import curry, pipe, compose, last, first
from core.price_handler.ccxt_historic import CCXTHistoricPriceHandler
from core.price_handler.ccxt_live import CCXTLivePriceHandler
import core.price_handler as price_handler
import queue
import collections
import itertools
import time
import asyncio
from core.trading_session import TradingSession
import numpy as np
import talib
from talib import abstract
from enum import Enum
from core.strategy.EMA_cross import EMACrossStrategy
from core.event import BarEvent
from aiohttp import web
import aiohttp
from core.utils.json_encoder import JSONEncoder
import json
import websockets
import core.strategy as strategy
import pkgutil
import core.configuration as configuration
import aiohttp_cors
import ccxt.async as ccxt

# timeframes
# symbols
# currencies
# name

# supported_exchanges = ['binance', 'gdax', 'kraken', 'poloniex']
supported_exchanges = ['binance', 'gdax']
# supported_coins = ['BTC', 'ETH', 'BCH', 'LTC', 'USDT', 'USD', 'EUR']


async def get_exchanges(request):
    # print(request.query)
    # if 'test' in request.query:
    #     print(request.query['test'])
    #     print('works!!!')
    return web.json_response(supported_exchanges)


async def load_exchange(request):
    if 'name' in request.query:
        return web.json_response(CCXT.load_market_data(request.name),
                                 dumps=JSONEncoder().default)


def get_currencies(symbols):
    currencies = {}
    base_currencies = {}

    for symbol in symbols:
        coins = symbol.split('/')

        if coins and len(coins) == 2:
            if coins[0] not in currencies:
                currencies[coins[0]] = []
            if coins[1] not in currencies:
                currencies[coins[1]] = []

            currencies[coins[0]].append(coins[1])
            currencies[coins[1]].append(coins[0])
            base_currencies[coins[1]] = True

    return {
        'currencies': currencies,
        'base_currencies': compose(list)(base_currencies.keys())
    }


async def get_market(request):
    algorithms = configuration.get_algorithms()
    exchanges_data = {}

    for exchange in supported_exchanges:
        exchanges_data[exchange] = await CCXT.load_market_data(exchange)

        if exchange in exchanges_data:
            symbols = exchanges_data[exchange]['symbols']
            exchanges_data[exchange]['currencies'] = get_currencies(symbols)
    exchange = exchanges_data[supported_exchanges[0]]
    # if 'name' in request.query:
    #     exchange = await CCXT.load_market_data(request.name)
    # else:
    #     print('on binance')
    #     exchange = await CCXT.load_market_data('binance')

    return web.json_response({
        "exchanges_data": exchanges_data,
        "exchanges": compose(list)(exchanges_data.keys()),
        "algorithms": algorithms
    },
        dumps=JSONEncoder().default
    )


def event_processor(event):
    print('event_processor', event)


async def backtest(request):
    print(request)
    # tickers = ['BTC/USD', 'ETH/USD']
    tickers = ['BTC/USDT', 'ETH/USDT']

    loop = asyncio.get_event_loop()
    binance = await CCXT.create('binance')
    start_dt = datetime.datetime(2018, 1, 1)
    end_dt = datetime.datetime(2018, 1, 2)
    events_queue = asyncio.Queue()
    ema_strategy = EMACrossStrategy(tickers, events_queue, 2, 4)
    s = await TradingSession.create(binance, tickers, events_queue,
                                    ema_strategy, 1000, 'USDT',
                                    start_dt, end_dt,
                                    timeframe="4h",
                                    price_handler='ccxt_historic'
                                    # session_type='live',
                                    # end_date=datetime.datetime(2018, 5, 14)
                                    )
    report = await s.run_session()
    await binance.close()

    return web.json_response(report, dumps=JSONEncoder().default)


async def live_session(request):
    print(request)
    # tickers = ['BTC/USD', 'ETH/USD']
    tickers = ['BTC/USDT', 'ETH/USDT']

    loop = asyncio.get_event_loop()
    binance = await CCXT.create('binance')
    events_queue = asyncio.Queue()
    ema_strategy = EMACrossStrategy(tickers, events_queue, 2, 4)
    s = await TradingSession.create(binance, tickers, events_queue,
                                    ema_strategy, 1000, 'USDT',
                                    timeframe="1m",
                                    session_type='live',
                                    end_date=datetime.datetime(
                                        2018, 5, 17, 22, 34)
                                    )
    print('before report event_processor:', event_processor)
    report = await s.run_session(event_processor)
    await binance.close()

    return web.json_response(report, dumps=JSONEncoder().default)


async def get_algorithms(request):
    modules = configuration.get_algorithms()
    return web.json_response(modules)


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


async def callback(msg):
    print(msg)


async def websocket(session):
    async with session.ws_connect('http://0.0.0.0:8080') as ws:
        async for msg in ws:
            await ws.send_str('testing send str')
            if msg.type == aiohttp.WSMsgType.TEXT:
                await callback(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break


async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(message)


# Configure default CORS settings.
def setup_cors(app):
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    return cors


def start_server(args):
    app = web.Application()
    app.router.add_get('/backtest', backtest)
    app.router.add_get('/live_session', live_session)
    app.router.add_get('/get_algorithms', get_algorithms)
    app.router.add_get('/get_exchanges', get_exchanges)
    app.router.add_get('/load_exchange', load_exchange)
    app.router.add_get('/get_market', get_market)
    # Configure CORS on all routes.
    setup_cors(app)

    # app.router.add_get('/ws', websocket_handler)
    # app.router.add_get('/ws_client', websocket_handler)
    # app.on_startup.append(init)

    # web.run_app(app)
    # asyncio.get_event_loop().run_until_complete(
    #     websockets.serve(echo, '0.0.0.0', 8080))
    # asyncio.get_event_loop().run_forever()
    return app
