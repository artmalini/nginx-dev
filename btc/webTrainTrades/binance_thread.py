from connectionInstanceBinance import ConnectionInstanceBinance
from connectionInstanceBinanceSpot import ConnectionInstanceBinanceSpot
# from V1BinanceBot import V1BinanceBot
from V1BinanceBotSpot import V1BinanceBotSpot
import threading
import helpers as h
import time

SENTINEL = None
connectBin = None
useBinanceBot = None

def process_binance_request(data, exit_event, binance_queue, mainqueu):
    global connectBin
    global useBinanceBot
    # Process Binance request
    try:
        # if "spot" not in data :
            # connectBin = ConnectionInstanceBinance(testnet=h.ENABLE_TESTING)
            # if connectBin.binance_us_websocket_api_manager and connectBin.client:
            #     useBinanceBot = V1BinanceBot(data, connectBin.client, connectBin.binance_us_websocket_api_manager)
            #     useBinanceBot.start(connectBin.api_key, connectBin.api_secret) 
            #     connectBin.closeBinanceStreamConnection()
            #     del useBinanceBot
            #     del connectBin
        if "spot" in data :
            connectBin = ConnectionInstanceBinanceSpot(testnet=h.ENABLE_TESTING)
            useBinanceBot = V1BinanceBotSpot(data, connectBin.client, connectBin.binance_us_websocket_api_manager)
            useBinanceBot.start(connectBin.api_key, connectBin.api_secret, exit_event, binance_queue, mainqueu)
            # suseBinanceBot.playAlgo(binance_queue)
    except Exception as e:
        h.logger.warning(f"An error occurred in process_binance_request: {e}")

def start_binance_thread(binance_queue, exit_event, mainqueu):
    global connectBin
    global useBinanceBot

    data = binance_queue.get()
    h.logger.info(f"Thread process_binance_request binance_queue: {data}, useBinanceBot {useBinanceBot}")

    if data is None:
        binance_queue.task_done()
        if connectBin:
            connectBin.closeBinanceStreamConnection()
            del connectBin
            connectBin = None
        if useBinanceBot:
            del useBinanceBot
            useBinanceBot = None
        # exit_event.set()
        # binance_queue.put(SENTINEL)
        h.logger.info(f"start_binance_thread exit with empty request: {None}")
        mainqueu["ready"] = True
        return

    if useBinanceBot is None and "algoTrade" in data and data["algoTrade"] == True:
        h.logger.info(f"First Initialize")
        process_binance_request(data, exit_event, binance_queue, mainqueu)
        # mainqueu["count"] += 1 
        return

    if useBinanceBot and "algoTrade" in data and data["algoTrade"] == False:
        h.logger.info(f"useBinanceBot {data}")
        useBinanceBot.setConfig(data)
        # useBinanceBot.playAlgo(exit_event, data)
        time.sleep(7)
        connectBin.closeBinanceStreamConnection()
        del useBinanceBot
        del connectBin
        useBinanceBot = None
        connectBin = None
        mainqueu["ready"] = True
        # exit_event.set()
        # binance_queue.put(SENTINEL)


        # exit_event.set()
        # binance_queue.put(SENTINEL)
    # if data is None:
    #     binance_queue.task_done()
    #     return
    # if data is SENTINEL:
    #     binance_queue.task_done()
    #     return
    # process_binance_request(data, binance_queue)
    # binance_queue.task_done()


    # try:
    #     while not exit_event.is_set():
    #         data = binance_queue.get()
    #         if data is None:
    #             binance_queue.task_done()
    #             break
    #         if data is SENTINEL:
    #             binance_queue.task_done()
    #             break
    #         process_binance_request(data, binance_queue)
    #         binance_queue.task_done()
    # except Exception as e:
    #     h.logger.warning(f"An error occurred in start_binance_thread: {e}")

def isInstanceAvailable():
    global connectBin
    global useBinanceBot

    if useBinanceBot and connectBin:
        return True
    return False
