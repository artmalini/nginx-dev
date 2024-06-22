import time
from datetime import datetime, timedelta
import logging
import os
import json
import binance_history as bh
import pandas as pd
import helpers as h
from visualGraph import visualGraph
import pickle
from pathlib import Path
from queue import Queue
import threading
from binance_thread import start_binance_thread, isInstanceAvailable

exchange_queue = Queue()
binance_queue = Queue()
SENTINEL = None
SEC_TO_MIN_TRY = 8
globalthreads = []
mainqueu = {
    "ready": False,
    "count": 0
}
trainedSource = None

# Configuration dictionary
# config = {
#     "stop": False
# }

pd.set_option('display.max_rows', None)  # Show all rows
# pd.set_option('display.max_columns', None)  # Show all columns

# CACHE_FILE = 'klines_cache.pkl'
# CACHE_FILE = "{path}/klines/{m5}/{fname}.pkl".format(path=os.path.dirname(os.path.abspath(__file__)), m5="m5", fname="klines_cache")

def klineDirectory(broker, start, end, symbol, timeframe):
    # Create directory if it doesn't exist
    directory_path = "{path}/klines/{broker}/{symbol}/{timefolder}".format(path=os.path.dirname(os.path.abspath(__file__)), broker=broker, symbol=symbol, timefolder=timeframe)
    try:
        os.makedirs(directory_path, exist_ok=True)
    except OSError as e:
        print("Error creating directory:", e)
        return os.path.dirname(os.path.abspath(__file__))

    # Generate filename
    converted_range = "{}_{}".format(start.replace(" ", "_"), end.replace(" ", "_"))
    converted_range = converted_range.replace(":", "-")  # Replace colon with hyphen
    file_path = "{}/{}.pkl".format(directory_path, converted_range)

    # Check if file exists
    if os.path.exists(file_path):
        print("File already exists:", file_path)
        return file_path

    # File doesn't exist, create it
    try:
        open(file_path, 'a').close()  # Create an empty file
        print("File created:", file_path)
        return file_path
    except OSError as e:
        print("Error creating file:", e)
        return os.path.dirname(os.path.abspath(__file__))
    
def load_cached_data(broker, start, end, symbol, timeframe):
    cacheFile = klineDirectory(broker, start, end, symbol, timeframe)
    if os.path.exists(cacheFile):
        try:
            with open(cacheFile, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading cached data: {e}")
    return None

def save_cached_data(klines, broker, start, end, symbol, timeframe):
    cacheFile = klineDirectory(broker, start, end, symbol, timeframe)
    with open(cacheFile, 'wb') as f:
        pickle.dump(klines, f)

# MAIN SCRIPT
def fetch_and_cache_klines(data, broker, start, end, symbol, timeframe):
    global trainedSource
    
    cached_data = load_cached_data(broker, start, end, symbol, timeframe)
    no_cached = True

    if cached_data is None :
        klines = bh.fetch_klines(
            asset_type="spot",
            symbol=symbol,
            timeframe=timeframe,
            start=start,
            end=end,
            tz="Europe/Kiev"
        )
        save_cached_data(klines, broker, start, end, symbol, timeframe)
        no_cached = False
    
    if no_cached == False:
        cached_data = load_cached_data(broker, start, end, symbol, timeframe)
    
    if cached_data is not None and not cached_data.empty:
        # print(cached_data.columns)
        # print(cached_data.head())

        if data["resetPreviousTraining"] == True :
            trainedSource = {}
        visual = visualGraph(cached_data, trainedSource)
        
        trainedSource = visual.start()
        h.logger.info(f'trainedSource {trainedSource}')

        # return cached_data
    return 'exit'
    
def process_exchange_requests():
    while True:
        data = exchange_queue.get()
        if data is SENTINEL:
            exchange_queue.task_done()
            break
        response= fetch_and_cache_klines(data, data["exchange"], data["startTime"], data["endTime"], data["symbol"], data["timeframe"])
        if response == 'exit':
            exchange_queue.task_done()
            break

def getProcessInputs():
    global globalthreads
    global trainedSource
    global mainqueu
    buffer_size = 1000

    # inputs = {
    #     "dateRange": False,
    #     "source": "open",
    #     "neighborsCount": 8,
    #     "maxBarsBack": 2000,
    #     "featureCount": 5,
    #     "featureSeries": {
    #         "f1_string": {"Feature": "RSI", "f1_paramA": 14, "f1_paramB": 1},
    #         "f2_string": {"Feature": "WT", "f1_paramA": 10, "f1_paramB": 11},
    #         "f3_string": {"Feature": "CCI", "f1_paramA": 20, "f1_paramB": 1},
    #         "f4_string": {"Feature": "ADX", "f1_paramA": 20, "f1_paramB": 1},
    #         "f5_string": {"Feature": "RSI1", "f1_paramA": 4, "f1_paramB": 1},
    #     },
    #     "useLorenzian": False,
    #     "useVSLRT": False,
    #     "useHLOOT": True,
    #     "useEma": False,
    #     "useSma": False,
    #     "useSUPERTREND": False,
    #     "useZeroLag": False,
    #     "useRTI": False,  
    #     "enableAO": False, 
    #     "enableHeikenAshi": False,
    #     "vslrtLen1": 20,
    #     "vslrtLen2": 50,
    #     "hlooSource": "open",
    #     "hlootLength": 2,
    #     "hlootPercent": 0.7,
    #     "hlootHllength": 53,
    #     "hlootMav": "VAR", 
    #     "useReverseOrderHLOOT": False,
    #     "emaSource": "open",
    #     "emalen": 8,
    #     "smaSource": "open",
    #     "smalen": 200,
    #     "superPrd": 2,
    #     "superFactor": 3,
    #     "superPd": 10,
    #     "useExitCrossZeroLag": False,
    #     "useEntryAboveBelowZeroLag": True,
    #     "smthtype": "Kaufman",
    #     "srcin": "open",
    #     "inpPeriodFast": 22,
    #     "inpPeriodSlow": 144,
    #     "useRTIrestrictObOs": False,
    #     "useRTImovingAverageCrossingRTI": True,
    #     "trendDataCount": 100,
    #     "trendSensitivityPercentage": 95,
    #     "signalLength": 20,
    #     "obRTI": 80,
    #     "osRT": 20,
    #     "lengthAO": 50,
    #     "sigLengthAO": 9,
    #     "lenFSM": 10,
    #     "len2SSM": 10
    # }

    # dump = json.dumps(inputs)
    # h.logger.info(f"JSON DUMP INPUTS: {dump}")

    # jsonSource = json.loads(dump)
    # h.logger.info(f"Convert from json back: {jsonSource}")

    # return
    # data = [{
    #     "exchange": "Binance",
    #     "training": True,
    #     "resetPreviousTraining": True,
    #     "algoTrade": True,
    #     "spot": True,
    #     "symbol": "BTCUSDT",
    #     "startTime": "2024-03-14 00:01",
    #     "endTime": "2024-04-27 00:01",
    #     "timeframe": "5m",
    #     "inputs": {}
    # },
    # {
    #     "exchange": "Binance",
    #     "training": False,
    #     "resetPreviousTraining": False,
    #     "algoTrade": False,
    #     "spot": True,
    #     "symbol": "BTCUSDT",
    #     "startTime": "2024-03-14 00:01",
    #     "endTime": "2024-04-27 00:01",
    #     "timeframe": "5m",
    #     "inputs": {}
    # },
    # {
    #     "exchange": "Binance",
    #     "training": True,
    #     "resetPreviousTraining": True,
    #     "algoTrade": True,
    #     "spot": True,
    #     "symbol": "ETHUSDT",
    #     "startTime": "2024-03-14 00:01",
    #     "endTime": "2024-04-27 00:01",
    #     "timeframe": "5m",
    #     "inputs": {}
    # },
    # {
    #     "exchange": "Binance",
    #     "training": False,
    #     "resetPreviousTraining": False,
    #     "algoTrade": False,
    #     "spot": True,
    #     "symbol": "ETHUSDT",
    #     "startTime": "2024-03-14 00:01",
    #     "endTime": "2024-04-27 00:01",
    #     "timeframe": "5m",
    #     "inputs": {}
    # }
    # ]

    data = [{
        "exchange": "Binance",
        "training": True,
        "resetPreviousTraining": True,
        "algoTrade": True,
        "spot": True,
        "symbol": "BTCUSDT",
        "startTime": "2024-03-14 00:01",
        "endTime": "2024-04-27 00:01",
        "timeframe": "5m",
        "inputs": {}
    }
    ]
    
    for item in data:
        exchange_queue.put(item)
        if item["training"] == 'True':
            # Start the threads for processing requests
            exchange_thread = threading.Thread(target=process_exchange_requests)
            exchange_thread.start()
            # Signal threads to exit
            exchange_queue.put(SENTINEL)
            # Wait for threads to finish
            exchange_thread.join()
        # return
        # Start algoTrading
        exit_event = threading.Event()
        item["trainedSource"] = trainedSource
        binance_queue.put(item)
        # if "algoTrade" in item and item["algoTrade"] == True :
        h.logger.info(f'MainTrainer put data: {item}')

    count = 0
    while True :
        if mainqueu["ready"] == False:
            binance_thread = threading.Thread(target=start_binance_thread, args=(binance_queue, exit_event, mainqueu))
            globalthreads.append(binance_thread)
            binance_thread.start()

            if "algoTrade" in item and item["algoTrade"] == False and len(globalthreads) > 1:
                time.sleep(30) 
                h.logger.info(f'globalthreads {len(globalthreads)}')
                for t in globalthreads:
                    h.logger.info(f'threads {t}')
                    t.join()
                globalthreads = []
        
        # if binance_queue.qsize() != 0:
        #     count = 0
        #     mainqueu["ready"] = False
        # if binance_queue.qsize() == 0:
        #     count = 0
        #     mainqueu["ready"] = False
        #     break
        time.sleep(25)
        h.logger.info(f'mainqueu: {mainqueu}')
        if mainqueu["ready"] == True:
            count += 1
            mainqueu["ready"] = False
            if binance_queue.qsize() == 0:
                break
        

    # if "algoTrade" in item and item["algoTrade"] == False and isInstanceAvailable() == False:
    #     h.logger.info(f'MainTrainer set exit to thread')
    #     exit_event.set()
    #     binance_queue.put(SENTINEL)
    #     binance_thread.join()
    #     return

    # ----------------------------------
    # Temp for data relay
    # time.sleep(30) 
    # h.logger.info('MainTrainer next delay 30s')

getProcessInputs()
#  except KeyboardInterrupt:


# klines = fetch_and_cache_klines("Binance", "2024-03-14 00:01", "2024-04-27 00:01", "BTCUSDT", "5m")
# h.logger.info(klines)



# klines = bh.fetch_klines(
#     asset_type="spot",
#     symbol="BTCUSDT",
#     timeframe="5m",
#     start="2023-09-14 00:01",
#     end="2023-12-24 00:01",
#     tz="Europe/Kiev"
# )

# logger.info(klines)