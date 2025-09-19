import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from technical_analysis import TechnicalAnalysis
from config import Config
import logging
from datetime import datetime

class TradingStrategy:
    def __init__(self):
        self.config = Config()
        self.ta = TechnicalAnalysis()
        self.logger = logging.getLogger(__name__)

    def generate_signals(self, symbol: str, data: pd.DataFrame) -> Dict[str, any]:
        """Generate trading signals based on technical analysis"""

        if len(data) < 50:  # Need sufficient data for analysis
            self.logger.warning(f"Insufficient data for {symbol}")
            return {'signal': 'NO_SIGNAL', 'reason': 'Insufficient data'}

        trend_analysis = self.ta.analyze_trend(data, self.config.EMA_PERIOD_SHORT, self.config.EMA_PERIOD_LONG)
        high_low_analysis = self.ta.get_high_low_analysis(data)

        signal_data = self._evaluate_signal(trend_analysis, high_low_analysis, symbol)

        return signal_data

    def _evaluate_signal(self, trend_analysis: Dict, high_low_analysis: Dict, symbol: str) -> Dict[str, any]:
        """Evaluate all conditions to generate final signal"""

        signal = 'NO_SIGNAL'
        signal_type = None
        confidence = 0
        reasons = []

        current_price = trend_analysis['current_price']
        trend = trend_analysis['trend']
        signal_strength = trend_analysis['signal_strength']
        rsi = trend_analysis['rsi']

        ema_short = trend_analysis['ema_short']
        ema_long = trend_analysis['ema_long']

        if (trend == 'BULLISH' and
            signal_strength >= 2 and
            rsi < 70 and  # Not overbought
            current_price > ema_short and
            ema_short > ema_long):

            signal = 'BUY_CALL'
            signal_type = 'CALL'
            confidence += 30
            reasons.append('Bullish EMA crossover')

            if high_low_analysis.get('high_breakout', False):
                confidence += 20
                reasons.append('High breakout')

            if rsi > 50 and rsi < 65:
                confidence += 15
                reasons.append('RSI in bullish zone')

            if trend_analysis['macd'] > trend_analysis['macd_signal']:
                confidence += 15
                reasons.append('MACD bullish')

        elif (trend == 'BEARISH' and
              signal_strength <= -2 and
              rsi > 30 and  # Not oversold
              current_price < ema_short and
              ema_short < ema_long):

            signal = 'BUY_PUT'
            signal_type = 'PUT'
            confidence += 30
            reasons.append('Bearish EMA crossover')

            if high_low_analysis.get('low_breakdown', False):
                confidence += 20
                reasons.append('Low breakdown')

            if rsi < 50 and rsi > 35:
                confidence += 15
                reasons.append('RSI in bearish zone')

            if trend_analysis['macd'] < trend_analysis['macd_signal']:
                confidence += 15
                reasons.append('MACD bearish')

        elif trend == 'NEUTRAL' and abs(signal_strength) <= 1:
            if high_low_analysis.get('range_expansion', False):
                if current_price > trend_analysis['bollinger_upper']:
                    signal = 'BUY_CALL'
                    signal_type = 'CALL'
                    confidence += 25
                    reasons.append('Bollinger upper breakout')
                elif current_price < trend_analysis['bollinger_lower']:
                    signal = 'BUY_PUT'
                    signal_type = 'PUT'
                    confidence += 25
                    reasons.append('Bollinger lower breakdown')

        stop_loss, target = self._calculate_levels(current_price, signal_type, trend_analysis)

        return {
            'symbol': symbol,
            'signal': signal,
            'signal_type': signal_type,
            'confidence': min(confidence, 100),  # Cap at 100%
            'current_price': current_price,
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'target': target,
            'reasons': reasons,
            'trend': trend,
            'rsi': rsi,
            'timestamp': datetime.now(),
            'risk_reward_ratio': self._calculate_risk_reward(current_price, stop_loss, target) if stop_loss and target else 0
        }

    def _calculate_levels(self, current_price: float, signal_type: Optional[str], trend_analysis: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Calculate stop loss and target levels"""

        if not signal_type:
            return None, None


        if signal_type == 'CALL':
            stop_loss = current_price * (1 - self.config.STOP_LOSS_PERCENT)
            target = current_price * (1 + self.config.TARGET_PROFIT_PERCENT)

            support = trend_analysis['support_resistance']['support']
            if support > stop_loss and support < current_price * 0.98:
                stop_loss = support

        elif signal_type == 'PUT':
            stop_loss = current_price * (1 + self.config.STOP_LOSS_PERCENT)
            target = current_price * (1 - self.config.TARGET_PROFIT_PERCENT)

            resistance = trend_analysis['support_resistance']['resistance']
            if resistance < stop_loss and resistance > current_price * 1.02:
                stop_loss = resistance

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

    def filter_signals(self, signals: List[Dict]) -> List[Dict]:
        """Filter signals based on risk management rules"""

        filtered_signals = []

        for signal in signals:
            if signal['signal'] == 'NO_SIGNAL':
                continue

            if signal['confidence'] < 60:
                self.logger.info(f"Signal filtered: Low confidence ({signal['confidence']}%) for {signal['symbol']}")
                continue

            if signal['risk_reward_ratio'] < 1.5:
                self.logger.info(f"Signal filtered: Poor risk-reward ratio ({signal['risk_reward_ratio']:.2f}) for {signal['symbol']}")
                continue

            signal['position_size'] = self._calculate_position_size(signal)

            filtered_signals.append(signal)

        return filtered_signals

    def _calculate_position_size(self, signal: Dict) -> float:
        """Calculate position size based on risk management"""


        risk_per_trade = self.config.MAX_RISK_PER_TRADE
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

    def get_option_recommendations(self, signals: List[Dict]) -> List[Dict]:
        """Convert signals to specific option recommendations"""

        recommendations = []

        for signal in signals:
            if signal['signal'] == 'NO_SIGNAL':
                continue

            symbol = signal['symbol']
            current_price = signal['current_price']
            signal_type = signal['signal_type']


            if signal_type == 'CALL':
                recommended_strike = self._round_to_strike(current_price * 1.01)
                option_type = 'CE'
            elif signal_type == 'PUT':
                recommended_strike = self._round_to_strike(current_price * 0.99)
                option_type = 'PE'
            else:
                continue

            expiry = self._get_nearest_expiry()
n            if ':' in symbol:
                base_symbol = symbol.split(':')[1].replace('-INDEX', '')
            else:
                base_symbol = symbol.replace('-INDEX', '')
            option_symbol = f"{base_symbol}{expiry}{recommended_strike}{option_type}"

            recommendation = {
                'underlying_symbol': symbol,
                'option_symbol': option_symbol,
                'strike_price': recommended_strike,
                'option_type': option_type,
                'action': 'BUY',
                'quantity': int(signal['position_size']),
                'confidence': signal['confidence'],
                'reasons': signal['reasons'],
                'stop_loss': signal['stop_loss'],
                'target': signal['target'],
                'risk_reward_ratio': signal['risk_reward_ratio'],
                'timestamp': signal['timestamp']
            }

            recommendations.append(recommendation)

        return recommendations

    def _round_to_strike(self, price: float) -> int:
        """Round price to nearest option strike"""
        return int(round(price / 50) * 50)

    def _get_nearest_expiry(self) -> str:
        """Get nearest Thursday expiry (simplified)"""
        from datetime import datetime, timedelta

        today = datetime.now()
        days_ahead = 3 - today.weekday()  # Thursday is 3
        if days_ahead <= 0:
            days_ahead += 7

        expiry_date = today + timedelta(days=days_ahead)
        return expiry_date.strftime("%y%b").upper()
