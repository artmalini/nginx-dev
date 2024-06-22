import json
from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
from unicorn_binance_rest_api.manager import BinanceRestApiManager, BinanceAPIException

TESTNET_WEBSOCKET_BINANCE = "binance.com-futures-testnet"
MAINNET_WEBSOCKET_BINANCE = "binance.com-futures"

TESTNET_BINANCE = "binance.com-testnet"
MAINNET_BINANCE = "binance.com"

class ConnectionInstanceBinance:
    def __init__(self, testnet=False):
        self.config = None
        self.testnet = testnet
        #  binance
        self.api_key = None
        self.api_secret = None
        self.binance_us_websocket_api_manager = None
        self.client = None
        
        self.loadConfig()
        self.processBinance()

    def loadConfig(self):
        # load config.json
        with open('config.json') as config_file:
            self.config = json.load(config_file)

    def processBinance(self):
        if 'BINANCE-FUTURES' in self.config['EXCHANGES']:
            if self.config['EXCHANGES']['BINANCE-FUTURES']['ENABLED']:
                print("Binance is enabled!")

            websocketApi = TESTNET_WEBSOCKET_BINANCE if self.testnet else MAINNET_WEBSOCKET_BINANCE
            urlApi = TESTNET_BINANCE if self.testnet else MAINNET_BINANCE

            self.binance_us_websocket_api_manager = BinanceWebSocketApiManager(exchange=websocketApi)

            if self.testnet == True :
                self.api_key = self.config['EXCHANGES']['BINANCE-FUTURES']['TEST']['API_KEY']
                self.api_secret = self.config['EXCHANGES']['BINANCE-FUTURES']['TEST']['API_SECRET']
                
                self.client = BinanceRestApiManager(
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    exchange=urlApi
                )
            if self.testnet == False :
                self.api_key = self.config['EXCHANGES']['BINANCE-FUTURES']['PROD']['API_KEY']
                self.api_secret = self.config['EXCHANGES']['BINANCE-FUTURES']['PROD']['API_SECRET']
                
                self.client = BinanceRestApiManager(
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    exchange=urlApi
                )

    def closeBinanceStreamConnection(self):
        self.binance_us_websocket_api_manager.stop_manager_with_all_streams()