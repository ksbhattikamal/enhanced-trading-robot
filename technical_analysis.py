import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging

class TechnicalAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    def calculate_sma(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = self.calculate_sma(data, period)
        std = data.rolling(window=period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    def calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD"""
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k': k_percent,
            'd': d_percent
        }
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def get_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        recent_data = data.tail(window)
        
        support = recent_data['low'].min()
        resistance = recent_data['high'].max()
        
        pivot = (recent_data['high'].iloc[-1] + recent_data['low'].iloc[-1] + recent_data['close'].iloc[-1]) / 3
        
        return {
            'support': support,
            'resistance': resistance,
            'pivot': pivot,
            'r1': 2 * pivot - recent_data['low'].iloc[-1],
            'r2': pivot + (recent_data['high'].iloc[-1] - recent_data['low'].iloc[-1]),
            's1': 2 * pivot - recent_data['high'].iloc[-1],
            's2': pivot - (recent_data['high'].iloc[-1] - recent_data['low'].iloc[-1])
        }
    
    def analyze_trend(self, data: pd.DataFrame, short_ema: int = 9, long_ema: int = 21) -> Dict[str, any]:
        """Analyze trend using multiple indicators"""
        close_prices = data['close']
        
        ema_short = self.calculate_ema(close_prices, short_ema)
        ema_long = self.calculate_ema(close_prices, long_ema)
        
        rsi = self.calculate_rsi(close_prices)
        macd = self.calculate_macd(close_prices)
        bollinger = self.calculate_bollinger_bands(close_prices)
        
        current_price = close_prices.iloc[-1]
        current_ema_short = ema_short.iloc[-1]
        current_ema_long = ema_long.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd['macd'].iloc[-1]
        current_signal = macd['signal'].iloc[-1]
        
        trend = "NEUTRAL"
        if current_ema_short > current_ema_long and current_price > current_ema_short:
            trend = "BULLISH"
        elif current_ema_short < current_ema_long and current_price < current_ema_short:
            trend = "BEARISH"
        
        signal_strength = 0
        
        if current_ema_short > current_ema_long:
            signal_strength += 1
        else:
            signal_strength -= 1
        
        if current_rsi > 70:
            signal_strength -= 1  # Overbought
        elif current_rsi < 30:
            signal_strength += 1  # Oversold
        
        if current_macd > current_signal:
            signal_strength += 1
        else:
            signal_strength -= 1
        
        return {
            'trend': trend,
            'signal_strength': signal_strength,
            'current_price': current_price,
            'ema_short': current_ema_short,
            'ema_long': current_ema_long,
            'rsi': current_rsi,
            'macd': current_macd,
            'macd_signal': current_signal,
            'bollinger_upper': bollinger['upper'].iloc[-1],
            'bollinger_lower': bollinger['lower'].iloc[-1],
            'support_resistance': self.get_support_resistance(data)
        }
    
    def get_high_low_analysis(self, data: pd.DataFrame) -> Dict[str, float]:
        """Analyze current and previous day high/low"""
        if len(data) < 2:
            return {}
        
        current_high = data['high'].iloc[-1]
        current_low = data['low'].iloc[-1]
        current_close = data['close'].iloc[-1]
        
        prev_high = data['high'].iloc[-2]
        prev_low = data['low'].iloc[-2]
        prev_close = data['close'].iloc[-2]
        
        current_range = current_high - current_low
        prev_range = prev_high - prev_low
        
        return {
            'current_high': current_high,
            'current_low': current_low,
            'current_close': current_close,
            'current_range': current_range,
            'prev_high': prev_high,
            'prev_low': prev_low,
            'prev_close': prev_close,
            'prev_range': prev_range,
            'high_breakout': current_close > prev_high,
            'low_breakdown': current_close < prev_low,
            'range_expansion': current_range > prev_range * 1.2,
            'range_contraction': current_range < prev_range * 0.8
        }
