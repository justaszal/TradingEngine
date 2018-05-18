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


async def run_session(request):
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


async def algorithms(request):
    strategy_package = configuration.import_core_package('strategy')
    risk_manager_package = configuration.import_core_package('risk_manager')
    modules = configuration.get_packages_modules(
        [strategy_package, risk_manager_package], True)
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


def start_server(args):
    app = web.Application()
    app.router.add_get('/backtest', backtest)
    app.router.add_get('/run_session', run_session)
    app.router.add_get('/algorithms', algorithms)
    # app.router.add_get('/ws', websocket_handler)
    # app.router.add_get('/ws_client', websocket_handler)
    # app.on_startup.append(init)

    # web.run_app(app)
    # asyncio.get_event_loop().run_until_complete(
    #     websockets.serve(echo, '0.0.0.0', 8080))
    # asyncio.get_event_loop().run_forever()
    return app
