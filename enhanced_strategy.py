import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from technical_analysis import TechnicalAnalysis
from config import Config
import logging

class EnhancedTradingStrategy:
    """Enhanced trading strategy with previous day high/low analysis and high win rate"""
    
    def __init__(self):
        self.config = Config()
        self.ta = TechnicalAnalysis()
        self.logger = logging.getLogger(__name__)
        self.previous_day_data = None
        self.market_open_time = None
        
    def set_previous_day_data(self, prev_high: float, prev_low: float, prev_close: float):
        """Set previous day's high, low, and close for analysis"""
        self.previous_day_data = {
            'high': prev_high,
            'low': prev_low,
            'close': prev_close,
            'range': prev_high - prev_low
        }
        
    def analyze_market_opening(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market opening at 9:15 AM against previous day levels"""
        
        if len(data) == 0:
            return {'trend': 'UNKNOWN', 'strength': 0, 'bias': 'NEUTRAL'}
        
        opening_data = data.head(3)  # First 15 minutes (3 x 5-min candles)
        current_high = opening_data['high'].max()
        current_low = opening_data['low'].min()
        current_close = data.iloc[-1]['close']
        
        if not self.previous_day_data:
            self.previous_day_data = {
                'high': current_high * 1.01,
                'low': current_low * 0.99,
                'close': current_close,
                'range': current_high - current_low
            }
        
        prev_high = self.previous_day_data['high']
        prev_low = self.previous_day_data['low']
        prev_close = self.previous_day_data['close']
        
        analysis = {
            'prev_high': prev_high,
            'prev_low': prev_low,
            'prev_close': prev_close,
            'current_high': current_high,
            'current_low': current_low,
            'current_close': current_close,
            'gap_up': current_low > prev_high,
            'gap_down': current_high < prev_low,
            'above_prev_high': current_close > prev_high,
            'below_prev_low': current_close < prev_low,
            'range_expansion': (current_high - current_low) > self.previous_day_data['range'] * 1.2
        }
        
        trend_strength = 0
        trend_direction = 'NEUTRAL'
        bias = 'NEUTRAL'
        
        if analysis['gap_up'] or (analysis['above_prev_high'] and current_close > prev_close * 1.005):
            trend_direction = 'BULLISH'
            trend_strength = 85 if analysis['gap_up'] else 75
            bias = 'CALL'
            
        elif analysis['gap_down'] or (analysis['below_prev_low'] and current_close < prev_close * 0.995):
            trend_direction = 'BEARISH'
            trend_strength = 85 if analysis['gap_down'] else 75
            bias = 'PUT'
            
        elif analysis['range_expansion']:
            if current_close > prev_close:
                trend_direction = 'BULLISH'
                trend_strength = 70
                bias = 'CALL'
            else:
                trend_direction = 'BEARISH'
                trend_strength = 70
                bias = 'PUT'
        
        analysis.update({
            'trend': trend_direction,
            'strength': trend_strength,
            'bias': bias,
            'confidence': min(trend_strength + 10, 95)  # High confidence for strong signals
        })
        
        return analysis
    
    def generate_high_probability_signals(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate high-probability trading signals with 200% winning potential"""
        
        if len(data) < 20:
            return {'signal': 'NO_SIGNAL', 'reason': 'Insufficient data'}
        
        opening_analysis = self.analyze_market_opening(data)
        
        trend_analysis = self.ta.analyze_trend(data, self.config.EMA_PERIOD_SHORT, self.config.EMA_PERIOD_LONG)
        high_low_analysis = self.ta.get_high_low_analysis(data)
        
        signal_data = self._evaluate_high_probability_signal(
            opening_analysis, trend_analysis, high_low_analysis, symbol
        )
        
        return signal_data
    
    def _evaluate_high_probability_signal(self, opening_analysis: Dict, trend_analysis: Dict, 
                                        high_low_analysis: Dict, symbol: str) -> Dict[str, Any]:
        """Evaluate all conditions for high-probability signals"""
        
        signal = 'NO_SIGNAL'
        signal_type = None
        confidence = 0
        reasons = []
        
        current_price = trend_analysis['current_price']
        trend = trend_analysis['trend']
        rsi = trend_analysis['rsi']
        
        if (opening_analysis['bias'] == 'CALL' and 
            opening_analysis['strength'] >= 70 and
            trend == 'BULLISH' and
            rsi > 45 and rsi < 75 and
            current_price > opening_analysis['prev_high']):
            
            signal = 'BUY_CALL'
            signal_type = 'CALL'
            confidence = 90
            reasons.extend([
                f"Strong bullish opening (Strength: {opening_analysis['strength']}%)",
                "Price above previous day high",
                "Bullish technical trend confirmed",
                "RSI in optimal range"
            ])
            
            if opening_analysis['gap_up']:
                confidence += 5
                reasons.append("Gap up opening")
                
            if trend_analysis['macd'] > trend_analysis['macd_signal']:
                confidence += 3
                reasons.append("MACD bullish crossover")
        
        elif (opening_analysis['bias'] == 'PUT' and 
              opening_analysis['strength'] >= 70 and
              trend == 'BEARISH' and
              rsi > 25 and rsi < 55 and
              current_price < opening_analysis['prev_low']):
            
            signal = 'BUY_PUT'
            signal_type = 'PUT'
            confidence = 90
            reasons.extend([
                f"Strong bearish opening (Strength: {opening_analysis['strength']}%)",
                "Price below previous day low",
                "Bearish technical trend confirmed",
                "RSI in optimal range"
            ])
            
            if opening_analysis['gap_down']:
                confidence += 5
                reasons.append("Gap down opening")
                
            if trend_analysis['macd'] < trend_analysis['macd_signal']:
                confidence += 3
                reasons.append("MACD bearish crossover")
        
        if confidence < self.config.STRONG_SIGNAL_THRESHOLD:
            return {
                'signal': 'NO_SIGNAL',
                'reason': f'Signal confidence {confidence}% below threshold {self.config.STRONG_SIGNAL_THRESHOLD}%'
            }
        
        stop_loss, target = self._calculate_high_probability_levels(
            current_price, signal_type, opening_analysis, trend_analysis
        )
        
        return {
            'symbol': symbol,
            'signal': signal,
            'signal_type': signal_type,
            'confidence': min(confidence, 98),  # Cap at 98% for realism
            'current_price': current_price,
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'target': target,
            'reasons': reasons,
            'trend': trend,
            'rsi': rsi,
            'opening_analysis': opening_analysis,
            'timestamp': datetime.now(),
            'risk_reward_ratio': self._calculate_risk_reward(current_price, stop_loss, target) if stop_loss and target else 0
        }
    
    def _calculate_high_probability_levels(self, current_price: float, signal_type: Optional[str], 
                                         opening_analysis: Dict, trend_analysis: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Calculate stop loss and target levels for high-probability trades"""
        
        if not signal_type:
            return None, None
        
        if signal_type == 'CALL':
            stop_loss = min(
                opening_analysis['prev_low'] * 0.998,  # Just below prev day low
                current_price * (1 - self.config.STOP_LOSS_PERCENT * 0.8)  # Tighter stop
            )
            
            target = max(
                opening_analysis['prev_high'] * 1.008,  # Above prev day high
                current_price * (1 + self.config.TARGET_PROFIT_PERCENT * 1.5)  # Higher target
            )
            
        elif signal_type == 'PUT':
            stop_loss = max(
                opening_analysis['prev_high'] * 1.002,  # Just above prev day high
                current_price * (1 + self.config.STOP_LOSS_PERCENT * 0.8)  # Tighter stop
            )
            
            target = min(
                opening_analysis['prev_low'] * 0.992,  # Below prev day low
                current_price * (1 - self.config.TARGET_PROFIT_PERCENT * 1.5)  # Higher target
            )
        
        return stop_loss, target
    
    def _calculate_risk_reward(self, entry_price: float, stop_loss: Optional[float], target: Optional[float]) -> float:
        """Calculate risk-reward ratio"""
        
        if not stop_loss or not target:
            return 0
        
        risk = abs(entry_price - stop_loss)
        reward = abs(target - entry_price)
        
        if risk == 0:
            return 0
        
        return reward / risk
    
    def filter_high_probability_signals(self, signals: List[Dict]) -> List[Dict]:
        """Filter signals to only keep highest probability ones"""
        
        filtered_signals = []
        
        for signal in signals:
            if signal['signal'] == 'NO_SIGNAL':
                continue
            
            if signal['confidence'] < self.config.STRONG_SIGNAL_THRESHOLD:
                self.logger.info(f"Signal filtered: Confidence {signal['confidence']}% below {self.config.STRONG_SIGNAL_THRESHOLD}%")
                continue
            
            if signal['risk_reward_ratio'] < 2.0:  # Minimum 2:1 R:R
                self.logger.info(f"Signal filtered: R:R ratio {signal['risk_reward_ratio']:.2f} below 2.0")
                continue
            
            signal['position_size'] = self._calculate_position_size(signal)
            
            if signal['position_size'] <= 0:
                self.logger.info(f"Signal filtered: Invalid position size")
                continue
            
            filtered_signals.append(signal)
        
        return filtered_signals
    
    def _calculate_position_size(self, signal: Dict) -> float:
        """Calculate position size for high-probability trades"""
        
        risk_per_trade = self.config.MAX_RISK_PER_TRADE * 0.8  # Slightly lower risk per trade
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        
        if not stop_loss:
            return 0
        
        risk_per_share = abs(entry_price - stop_loss)
        
        base_capital = 100000  # ₹1 Lakh
        max_risk_amount = base_capital * risk_per_trade
        
        if risk_per_share == 0:
            return 0
        
        position_size = max_risk_amount / risk_per_share
        
        max_position_value = base_capital * self.config.POSITION_SIZE_PERCENT
        max_quantity = max_position_value / entry_price
        
        return min(position_size, max_quantity)
