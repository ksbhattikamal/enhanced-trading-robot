import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FYERS_APP_ID = os.getenv('FYERS_APP_ID')
    FYERS_APP_SECRET = os.getenv('FYERS_APP_SECRET')
    FYERS_ACCESS_TOKEN = os.getenv('FYERS_ACCESS_TOKEN')
    FYERS_CLIENT_ID = os.getenv('FYERS_CLIENT_ID')
    
    SYMBOLS = {
        'NIFTY': 'NSE:NIFTY50-INDEX',
        'BANKNIFTY': 'NSE:NIFTYBANK-INDEX',
        'FINNIFTY': 'NSE:FINNIFTY-INDEX'
    }
    
    MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', 0.02))
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 0.05))
    POSITION_SIZE_PERCENT = float(os.getenv('POSITION_SIZE_PERCENT', 0.1))
    
    EMA_PERIOD_SHORT = int(os.getenv('EMA_PERIOD_SHORT', 9))
    EMA_PERIOD_LONG = int(os.getenv('EMA_PERIOD_LONG', 21))
    
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 0.015))
    TARGET_PROFIT_PERCENT = float(os.getenv('TARGET_PROFIT_PERCENT', 0.03))
    
    BASE_URL = "https://api-t1.fyers.in"
    DATA_URL = f"{BASE_URL}/data"
    API_URL = f"{BASE_URL}/api/v3"
