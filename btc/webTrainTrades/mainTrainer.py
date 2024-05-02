import time
from datetime import datetime, timedelta
import logging
import os
import json
import threading
import binance_history as bh
import pandas as pd
import helpers as h
from visualGraph import visualGraph
import pickle
from pathlib import Path

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

def fetch_and_cache_klines(broker, start, end, symbol, timeframe):
    cached_data = load_cached_data(broker, start, end, symbol, timeframe)
    
    if cached_data is not None and not cached_data.empty:
        # print(cached_data.columns)
        # print(cached_data.head())
        visual = visualGraph(cached_data)
        
        visual.start()
        return cached_data
    else:
        klines = bh.fetch_klines(
            asset_type="spot",
            symbol=symbol,
            timeframe=timeframe,
            start=start,
            end=end,
            tz="Europe/Kiev"
        )
        save_cached_data(klines, broker, start, end, symbol, timeframe)
        return klines
    
klines = fetch_and_cache_klines("Binance", "2024-03-14 00:01", "2024-04-27 00:01", "BTCUSDT", "5m")
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