import time
from datetime import datetime, timedelta
import logging
import os
import json
import threading
import queue
import re
import helpers as h
import random as random
import pandas as pd



SENTINEL = None
SEC_TO_MIN_TRY = 8
SEC_TO_TRY = 60
SEC_TO_PROCESS = 180
MAX_AMOUNT = 10000
STOCK_FEE = 0.00075

class V1BinanceBotSpot:
    def __init__(self, data, client, binance_us_websocket_api_manager):
        self.data = data
        self.client = client
        self.binance_us_websocket_api_manager = binance_us_websocket_api_manager
        self.pair = self.setPair()
        self.apikey = None
        self.apisecret = None
        # Configuration dictionary
        self.config = {
            "algoTrade": True
        }
        self.df = pd.DataFrame()
        self.tempRand = random.random()
        # Calculate the time difference between server and local time
        self.server_time = self.checkServerTime()
        self.server_time_dt = datetime.fromtimestamp(self.server_time['serverTime'] / 1000.0)
        self.time_offset = self.server_time_dt - datetime.utcnow()
        h.logger.info(f'Server time: {self.server_time_dt}, Local UTC time: {datetime.utcnow()}, Time offset: {self.time_offset}')

    def checkServerTime(self):
        attempt = 0
        while True and attempt < SEC_TO_TRY :
            try:
                server_request = self.client.get_server_time()
                if not 'serverTime' in server_request:
                    time.sleep(1)
                    attempt += 1
                    continue
                return server_request
            except Exception as e:
                h.logger.info(e)
                time.sleep(1)
                attempt += 1

    def get_synchronized_time(self):
        return datetime.utcnow() + self.time_offset
    
    def update_config(self, new_config):
        self.config.update(new_config)

    def setPair(self):
        pair = []

        pair.append({
                'isLoad': True,
                'wallet': 0,
                'name': self.data['symbol'].upper(),
                'base_asset_precision': 0,
                'use_bnb': 'No',
                'taker_fee': 0, 
                'maker_fee': 0,
                'stock_fee': 0,
                'price_filter': {
                    'tick_size': 0
                },
                'lot_size_filter': {
                    'max_trading_qty': 0, 
                    'min_trading_qty': 0, 
                    'qty_step': 0, 
                },
                'money_ammount': 0,
                'price_type': 'percent',
                'fails_count': 0,
                'wait_secconds': 300,
                'delay_replace': 5,
                'entered_price': 0,
                'max_price_alltitude': 0,
                'stop_high': 0.03,
                'sl_delta_percent': 0.15,
                'close_type': 'Full',
                'close_percent_ammount': 0,
                'init_order_quantity': 0,
                'orders_store': [],
                'market_close': "False",
                'order_book': [],
                'order_bookSell': [],
                'order_bookBuy': [],
                'limit_execute': False,
                'is_process_limit': 1,
                'instrument_info': {'last_price': 0},
                'kline': {
                    'start': 0,
                    'end': 0,
                    'o': 0,
                    'c': 0,
                    'h': 0,
                    'l': 0
                },
                'currentKlineStart': 0
            })
        for key in range(len(pair)):
            if 'use_bnb' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['use_bnb'] = self.data['use_bnb']
            if 'money_ammount' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['money_ammount'] = self.data['money_ammount']
            if 'price_type' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['price_type'] = self.data['price_type']
            if 'wait_secconds' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['wait_secconds'] = int(self.data['wait_secconds'])
            if 'delay_replace' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['delay_replace'] = int(self.data['delay_replace'])
            if 'stop_high' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['stop_high'] = float(self.data['stop_high'])
            if 'close_type' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['close_type'] = self.data['close_type']
            if 'market_close' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['market_close'] = self.data['market_close']
            if 'sl_delta_percent' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['sl_delta_percent'] = self.data['sl_delta_percent']
            if 'close_percent_ammount' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['close_percent_ammount'] = float(self.data['close_percent_ammount'])
            if 'type' in self.data and pair[key]['name'] == self.data['symbol']:
                pair[key]['type'] = self.data['type']
        return pair

    def handleInstrumentInfo(self, priceMsgChange):
        try:
            if len(priceMsgChange) > 0 :
                if priceMsgChange['symbol']:
                    for key in range(len(self.pair)):
                        if priceMsgChange['symbol'] == self.pair[key]['name']:
                            self.pair[key]['instrument_info']['last_price'] = float(priceMsgChange['price'])
        except Exception as e:
            h.logger.warning(e)
                    
    def handleKlineInfo(self, pair) :
        attempt = 0
        result = None
        while True and attempt < SEC_TO_TRY :
            try:
                result = self.client.get_klines(symbol=pair['name'], interval='5m', limit=4)
                if len(result) > 0:
                    last_kline = result[-1]
                    index = 0
                    for kline in result:
                        if kline[0] == pair['currentKlineStart'] and index > 0:
                            last_kline = kline # result[index - 1]
                            break
                        index +=1

                    if last_kline[0] == result[-1][0]:
                        h.logger.info(f"same kline as previous, need to check it again: {last_kline[1]}")
                        attempt += 1
                        time.sleep(1)
                        continue

                    # save most recent kline start
                    pair['currentKlineStart'] = result[-1][0]

                    pair['kline']['start'] = last_kline[0]
                    pair['kline']['end'] = last_kline[6]
                    pair['kline']['o'] = float(last_kline[1])
                    pair['kline']['c'] = float(last_kline[4])
                    pair['kline']['h'] = float(last_kline[2])
                    pair['kline']['l'] = float(last_kline[3])
                    return pair

            except Exception as e:
                h.logger.error(f"Error fetching kline data: {e} {result}")
                attempt += 1
                time.sleep(1)
                continue
        # try:
        #     for key in range(len(self.pair)):
        #         if data['s'] == self.pair[key]['name'] and self.pair[key]['kline']['start'] != data['t']:
        #             self.pair[key]['kline']['start'] = data['t']
        #             self.pair[key]['kline']['end'] = data['T']
        #             self.pair[key]['kline']['o'] = float(data['o'])
        #             self.pair[key]['kline']['c'] = float(data['c'])
        #             self.pair[key]['kline']['h'] = float(data['h'])
        #             self.pair[key]['kline']['l'] = float(data['l'])
        # except Exception as e:
        #     h.logger.warning(e)

    def handleOrderBook(self, depthUpdate):
        try:
            if len(depthUpdate) > 0 :
                symbolData = depthUpdate
                for key in range(len(self.pair)):
                        self.pair[key]['order_book'] = []
                        self.pair[key]['order_book'] = symbolData
                        if len(self.pair[key]['order_book']) > 0:
                            self.pair[key]['order_bookSell'] = symbolData['asks']
                            self.pair[key]['order_bookBuy'] = symbolData['bids']
        except Exception as e:
            h.logger.warning(e)

    def getSymbolInfo(self,symb,pair) :
        attempt = 0
        coinsResult = False
        while True and attempt < SEC_TO_TRY :
            try:
                coinsResult = self.client.get_exchange_info()
            except Exception as e:
                h.logger.warning(f"Coin Futures Exception occured - {e}")
                attempt += 1
                time.sleep(1)
                continue
            try:
                if coinsResult == False:
                    attempt += 1
                    time.sleep(1)
                    continue
                data = next(filter(lambda x: x['symbol'] == (symb.upper()), coinsResult['symbols']))
                pair['base_asset_precision'] = data['baseAssetPrecision']
                # QTY step
                pair['price_filter']['tick_size'] = float(data['filters'][0]['tickSize'])
                #  'stepSize'
                pair['lot_size_filter']['qty_step'] = float(data['filters'][1]['stepSize'])
                # 'marketLotSize'
                pair['lot_size_filter']['max_trading_qty'] = float(data['filters'][1]['maxQty']) 
                pair['lot_size_filter']['min_trading_qty'] = float(data['filters'][1]['minQty'])
                pair['taker_fee'] = 0.018 if pair['use_bnb'] != 'No' else 0.02
                pair['maker_fee'] = 0.036 if pair['use_bnb'] != 'No' else 0.04
                h.logger.info(data)
                h.logger.info(f"Pair for initialisation {pair}")
                return True
            except Exception as e:
                attempt += 1
                time.sleep(1)
                h.logger.info("getSymbolInfo Bad request", e)
        if attempt == SEC_TO_TRY :
            h.logger.critical("getSymbolInfo FAILURE")
            return -1
        
    def isBookStoreExist(self, pair): 
        if len(pair['order_bookBuy']) > 0 and len(pair['order_bookSell']) > 0 :
            return True
        return False
    
    def findPrice(self, pair):
        attempt = 0
        price = 0
        while True and attempt < SEC_TO_TRY :
            if self.isBookStoreExist(pair) == True:
                pair['fails_count'] = 0
                if self.data['side'] == 'Sell':
                    price = float(pair['order_bookSell'][0][0])
                if self.data['side'] == 'Buy':
                    price = float(pair['order_bookBuy'][0][0])
                break
            if price == 0:
                attempt += 1
                time.sleep(0.1)
                continue
        return price
    
    def run(self):
        pair = self.pair
        symbolInfo = -1
        for i in range(len(pair)):
            pair[i] = self.handleKlineInfo(pair[i])

            # if pair[i]['kline']['start'] != 0 and pair[i]['currentKlineStart'] != pair[i]['kline']['start']:
            # pair[i]['currentKlineStart'] = pair[i]['kline']['start']
            kline = {
                'open': [pair[i]['kline']['o']],
                'high': [pair[i]['kline']['h']],
                'low': [pair[i]['kline']['l']],
                'close': [pair[i]['kline']['c']],
                'close_datetime': [pd.to_datetime(pair[i]['kline']['start'], unit='ms')]
            }
            new_df = pd.DataFrame(kline)
            new_df.set_index('close_datetime', inplace=True)

            # Append new data to the existing DataFrame
            self.df = pd.concat([self.df, new_df])

            h.logger.info(self.df)
            h.logger.info('RUN main algo')
        

            time.sleep(1)
            # count +=1
        
           
        
    def is_empty_message(self, message):
        if message is False:
            return True
        if '"result":null' in message:
            return True
        if '"result":None' in message:
            return True
        return False
    
    def handle_price_change(self, symbol, timestamp, price):
        global symbolPriceTicker

        symbolPriceTicker = {'symbol':symbol,'timestamp':timestamp,'price':price}
        return symbolPriceTicker

    def process_stream_data(self, binance_websocket_api_manager): 
        while True:
            if binance_websocket_api_manager.is_manager_stopping():
                exit(0)
            oldest_data = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()

            is_empty = self.is_empty_message(oldest_data)
            if is_empty:
                time.sleep(0.01)
            else:
                oldest_data_dict = json.loads(oldest_data)
                data = oldest_data_dict['data']
                #  Handle price change
                priceMsgChange = ''
                if 'e' in data :
                    if 'trade' in data['e'] :
                        priceMsgChange = self.handle_price_change(symbol=data['s'], timestamp=data['T'], price=data['p'])
                        self.handleInstrumentInfo(priceMsgChange)
                    # if 'kline' in data['e'] :
                    #     self.handleKlineInfo(data['k'])
                        # print(data['k'])
                depthUpdate = ''
                if 'bids' in data :
                    depthUpdate = data
                    self.handleOrderBook(depthUpdate)

    def setConfig(self, data):
        h.logger.info(f'setConfig {data}')
        if "algoTrade" in data and data["algoTrade"] == False:
            h.logger.info(f'PLAY ALGO UPDATE CONFIG {data}')
            self.update_config(data)

    def playAlgo(self, exit_event, data):
        h.logger.info(f"head PLAY ALGO {self.data['symbol']} len(self.pair) {len(self.pair)} self.config {self.config}")
        # item = binance_queue.get()

        # h.logger.info(f'direct playAlgo {item}')
        # if isinstance(item, dict) and item["algoTrade"] == False:
        #     h.logger.info(f'PLAY ALGO UPDATE CONFIG {item}')
        #     self.update_config(item)

        h.logger.info(f"prepare to loop")
        stop = 0
        count = 0
        try:
            while (True and stop == 0):
                # remove pair if it's closed
                found = ''
                for key in range(len(self.pair)):
                    if self.config["algoTrade"] == False or self.pair[key]['isLoad'] == False :
                        h.logger.info(f'Is exit config["algoTrade"] {self.config}')
                        found = key

                if found != '':
                    h.logger.info(f"Fails number count {self.pair[key]['fails_count']}")
                    del self.pair[found]
                    del self.data
                    stop = 1

                if stop == 1 or len(self.pair) == 0 :
                    h.logger.info('Task completed logout ...')
                    time.sleep(1)
                    stop = 1
                    break
                
                if self.pair[key]['currentKlineStart'] == 0:
                    result = self.client.get_klines(symbol=self.pair[key]['name'], interval='5m', limit=4)
                    if result:
                        self.pair[key]['currentKlineStart'] = result[-1][0]

                # result = self.client.get_klines(symbol=self.pair[key]['name'], interval='5m', limit=4)
                # h.logger.info(f'klines {self.pair[key]["name"]} and: {result}')
                # return

                # Calculate time to next 5 minute interval
                now = self.get_synchronized_time()
                next_interval = (now + timedelta(minutes=5 - now.minute % 5)).replace(second=0, microsecond=0)
                sleep_duration = (next_interval - now).total_seconds()

                h.logger.info(f'sleep_duration: {sleep_duration} now: {now} next_interval: {next_interval}')
                # Wait until the next 5-minute interval
                if sleep_duration > 0:
                    time.sleep(sleep_duration)
                self.run()

                count += 1
                if count == 100:
                    self.pair[key]['isLoad'] = False

                # Check the queue for new configuration or sentinel
                # try:
                #     item = binance_queue.get(timeout=1)
                #     if item is SENTINEL:
                #         h.logger.info(f'binance_queue SENTINEL  {item}')
                #     if isinstance(item, dict):
                #         h.logger.info(f'UPDATE CONFIG {item}')
                #         self.update_config(item)
                # except queue.Empty:
                #     h.logger.info(f'Empty platAlgo queue')
                #     time.sleep(1)
                #     continue
               
        except Exception as e:
            h.logger.warning(e)
        
    def start(self, apikey, apisecret, exit_event, binance_queue, mainqueu):
        self.apikey = apikey
        self.apisecret = apisecret
        lc_symbols = []
        for key in range(len(self.pair)):
            lc_symbols.append(self.pair[key]['name'].lower())

        channels = ['trade','kline_5m']
        self.binance_us_websocket_api_manager.create_stream(channels, markets=lc_symbols, api_key=self.apikey, api_secret=self.apisecret, ping_interval=20, ping_timeout=20)

        # Start a worker process to move the received stream_data from the stream_buffer to a print function
        worker_thread = threading.Thread(target=self.process_stream_data, args=(self.binance_us_websocket_api_manager,))
        worker_thread.start()
        mainqueu["ready"] = True
        self.playAlgo(exit_event, binance_queue)
       