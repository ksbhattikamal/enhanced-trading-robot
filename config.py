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
    
    FOCUSED_SYMBOLS = {
        'NIFTY': ['NSE:NIFTY50-INDEX'],
        'BANKNIFTY': ['NSE:NIFTYBANK-INDEX'], 
        'FINNIFTY': ['NSE:FINNIFTY-INDEX'],
        'ALL': ['NSE:NIFTY50-INDEX', 'NSE:NIFTYBANK-INDEX', 'NSE:FINNIFTY-INDEX']
    }
    
    MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', 0.02))
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 0.05))
    POSITION_SIZE_PERCENT = float(os.getenv('POSITION_SIZE_PERCENT', 0.1))
    
    DAILY_PROFIT_TARGET = float(os.getenv('DAILY_PROFIT_TARGET', 1000))  # ₹1000 daily target
    DAILY_STOP_LOSS = float(os.getenv('DAILY_STOP_LOSS', 500))  # ₹500 daily stop loss
    AUTO_TRADING_ENABLED = os.getenv('AUTO_TRADING_ENABLED', 'true').lower() == 'true'
    FOCUS_SYMBOL = os.getenv('FOCUS_SYMBOL', 'NIFTY')  # Focus on NIFTY only
    
    MIN_WIN_RATE = float(os.getenv('MIN_WIN_RATE', 0.85))  # 85% minimum win rate
    STRONG_SIGNAL_THRESHOLD = float(os.getenv('STRONG_SIGNAL_THRESHOLD', 80))  # 80% confidence minimum
    ENHANCED_MODE = False  # Set to True for enhanced strategy
    
    EMA_PERIOD_SHORT = int(os.getenv('EMA_PERIOD_SHORT', 9))
    EMA_PERIOD_LONG = int(os.getenv('EMA_PERIOD_LONG', 21))
    
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 0.015))
    TARGET_PROFIT_PERCENT = float(os.getenv('TARGET_PROFIT_PERCENT', 0.03))
    
    BASE_URL = "https://api-t1.fyers.in"
    DATA_URL = f"{BASE_URL}/data"
    API_URL = f"{BASE_URL}/api/v3"
