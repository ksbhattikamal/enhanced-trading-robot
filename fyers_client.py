import logging
from fyers_apiv3 import fyersModel
from config import Config
import pandas as pd
from datetime import datetime, timedelta
import time

class FyersClient:
    def __init__(self):
        self.config = Config()
        self.client = None
        self.logger = self._setup_logger()
        self._initialize_client()
    
    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_robot.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _initialize_client(self):
        try:
            if not all([self.config.FYERS_CLIENT_ID, self.config.FYERS_ACCESS_TOKEN]):
                self.logger.error("Missing Fyers credentials. Please check your .env file.")
                return False
            
            self.client = fyersModel.FyersModel(
                client_id=self.config.FYERS_CLIENT_ID,
                access_token=self.config.FYERS_ACCESS_TOKEN,
                log_path="",
                log_level="ERROR"
            )
            
            profile = self.client.get_profile()
            if profile['s'] == 'ok':
                self.logger.info(f"Successfully connected to Fyers API for user: {profile['data']['name']}")
                return True
            else:
                self.logger.error(f"Failed to connect to Fyers API: {profile}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing Fyers client: {str(e)}")
            return False
    
    def get_historical_data(self, symbol, resolution="1", date_format=1, cont_flag=1, range_from=None, range_to=None):
        """
        Get historical data for a symbol
        resolution: 1, 2, 3, 5, 10, 15, 30, 45, 60, 120, 240, 1D
        """
        try:
            if not range_from:
                range_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            if not range_to:
                range_to = datetime.now().strftime("%Y-%m-%d")
            
            data = {
                "symbol": symbol,
                "resolution": resolution,
                "date_format": date_format,
                "range_from": range_from,
                "range_to": range_to,
                "cont_flag": cont_flag
            }
            
            response = self.client.history(data=data)
            
            if response['s'] == 'ok':
                candles = response['candles']
                df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('timestamp', inplace=True)
                return df
            else:
                self.logger.error(f"Error fetching historical data: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Exception in get_historical_data: {str(e)}")
            return None
    
    def get_quotes(self, symbols):
        """Get real-time quotes for symbols"""
        try:
            if isinstance(symbols, str):
                symbols = [symbols]
            
            data = {"symbols": ",".join(symbols)}
            response = self.client.quotes(data=data)
            
            if response['s'] == 'ok':
                return response['d']
            else:
                self.logger.error(f"Error fetching quotes: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Exception in get_quotes: {str(e)}")
            return None
    
    def get_market_depth(self, symbol):
        """Get market depth for a symbol"""
        try:
            data = {"symbol": symbol, "ohlcv_flag": 1}
            response = self.client.depth(data=data)
            
            if response['s'] == 'ok':
                return response['d']
            else:
                self.logger.error(f"Error fetching market depth: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Exception in get_market_depth: {str(e)}")
            return None
    
    def place_order(self, symbol, qty, side, type_order, product_type, limit_price=0, stop_price=0, disclosed_qty=0, order_tag="TradingRobot"):
        """
        Place an order
        side: 1 for Buy, -1 for Sell
        type_order: 1=Limit, 2=Market, 3=Stop(SL-M), 4=StopLimit(SL-L)
        product_type: CNC, INTRADAY, MARGIN, CO, BO
        """
        try:
            data = {
                "symbol": symbol,
                "qty": qty,
                "type": type_order,
                "side": side,
                "productType": product_type,
                "limitPrice": limit_price,
                "stopPrice": stop_price,
                "disclosedQty": disclosed_qty,
                "orderTag": order_tag,
                "validity": "DAY",
                "offlineOrder": False
            }
            
            response = self.client.place_order(data=data)
            
            if response['s'] == 'ok':
                self.logger.info(f"Order placed successfully: {response}")
                return response
            else:
                self.logger.error(f"Error placing order: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Exception in place_order: {str(e)}")
            return None
    
    def get_orderbook(self):
        """Get orderbook"""
        try:
            response = self.client.orderbook()
            
            if response['s'] == 'ok':
                return response['orderBook']
            else:
                self.logger.error(f"Error fetching orderbook: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Exception in get_orderbook: {str(e)}")
            return None
    
    def get_positions(self):
        """Get positions"""
        try:
            response = self.client.positions()
            
            if response['s'] == 'ok':
                return response['netPositions']
            else:
                self.logger.error(f"Error fetching positions: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Exception in get_positions: {str(e)}")
            return None
    
    def get_funds(self):
        """Get fund details"""
        try:
            response = self.client.funds()
            
            if response['s'] == 'ok':
                return response['fund_limit']
            else:
                self.logger.error(f"Error fetching funds: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Exception in get_funds: {str(e)}")
            return None
