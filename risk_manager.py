import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.daily_pnl = 0
        self.daily_trades = 0
        self.max_daily_trades = 10
        self.positions = {}
        self.trade_history = []
        self.daily_profit_target = getattr(config, 'DAILY_PROFIT_TARGET', 1000)
        self.daily_stop_loss = getattr(config, 'DAILY_STOP_LOSS', 500)
        self.profit_target_reached = False
        self.stop_loss_hit = False
    
    def check_risk_limits(self, signal: Dict, account_balance: float) -> Dict[str, any]:
        """Check if trade passes risk management rules"""
        
        risk_check = {
            'approved': True,
            'reasons': [],
            'adjusted_quantity': signal.get('quantity', 0)
        }
        
        if self.profit_target_reached or self.daily_pnl >= self.daily_profit_target:
            risk_check['approved'] = False
            self.profit_target_reached = True
            risk_check['reasons'].append(f'Daily profit target of ₹{self.daily_profit_target} reached (Current: ₹{self.daily_pnl:.2f})')
            return risk_check
        
        if self.stop_loss_hit or self.daily_pnl <= -self.daily_stop_loss:
            risk_check['approved'] = False
            self.stop_loss_hit = True
            risk_check['reasons'].append(f'Daily stop loss of ₹{self.daily_stop_loss} hit (Current: ₹{self.daily_pnl:.2f})')
            return risk_check
        
        if self.daily_pnl <= -account_balance * self.config.MAX_DAILY_LOSS:
            risk_check['approved'] = False
            risk_check['reasons'].append('Daily loss limit exceeded')
            return risk_check
        
        if self.daily_trades >= self.max_daily_trades:
            risk_check['approved'] = False
            risk_check['reasons'].append('Maximum daily trades limit reached')
            return risk_check
        
        entry_price = signal.get('entry_price', 0)
        quantity = signal.get('quantity', 0)
        position_value = entry_price * quantity
        
        max_position_value = account_balance * self.config.POSITION_SIZE_PERCENT
        
        if position_value > max_position_value:
            adjusted_quantity = int(max_position_value / entry_price)
            risk_check['adjusted_quantity'] = adjusted_quantity
            risk_check['reasons'].append(f'Position size adjusted from {quantity} to {adjusted_quantity}')
            
            if adjusted_quantity == 0:
                risk_check['approved'] = False
                risk_check['reasons'].append('Position size too small after adjustment')
        
        stop_loss = signal.get('stop_loss', 0)
        if stop_loss:
            risk_per_share = abs(entry_price - stop_loss)
            total_risk = risk_per_share * risk_check['adjusted_quantity']
            max_risk = account_balance * self.config.MAX_RISK_PER_TRADE
            
            if total_risk > max_risk:
                risk_adjusted_quantity = int(max_risk / risk_per_share)
                risk_check['adjusted_quantity'] = min(risk_check['adjusted_quantity'], risk_adjusted_quantity)
                risk_check['reasons'].append(f'Quantity adjusted for risk management to {risk_adjusted_quantity}')
                
                if risk_adjusted_quantity == 0:
                    risk_check['approved'] = False
                    risk_check['reasons'].append('Risk per trade too high')
        
        symbol = signal.get('underlying_symbol', '')
        if self._check_correlation_limits(symbol):
            risk_check['approved'] = False
            risk_check['reasons'].append('Too many correlated positions')
        
        return risk_check
    
    def _check_correlation_limits(self, symbol: str) -> bool:
        """Check if adding this position would exceed correlation limits"""
        
        index_family = self._get_index_family(symbol)
        family_positions = sum(1 for pos in self.positions.values() 
                             if self._get_index_family(pos.get('symbol', '')) == index_family)
        
        return family_positions >= 2
    
    def _get_index_family(self, symbol: str) -> str:
        """Get index family for correlation analysis"""
        if 'NIFTY' in symbol.upper():
            return 'NIFTY'
        elif 'BANK' in symbol.upper():
            return 'BANKNIFTY'
        elif 'FIN' in symbol.upper():
            return 'FINNIFTY'
        else:
            return 'OTHER'
    
    def add_position(self, trade_data: Dict):
        """Add a new position to tracking"""
        
        position_id = f"{trade_data['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.positions[position_id] = {
            'symbol': trade_data['symbol'],
            'quantity': trade_data['quantity'],
            'entry_price': trade_data['entry_price'],
            'stop_loss': trade_data.get('stop_loss'),
            'target': trade_data.get('target'),
            'entry_time': datetime.now(),
            'status': 'OPEN',
            'pnl': 0
        }
        
        self.daily_trades += 1
        self.logger.info(f"Position added: {position_id}")
        
        return position_id
    
    def update_position_pnl(self, position_id: str, current_price: float):
        """Update position P&L"""
        
        if position_id not in self.positions:
            return
        
        position = self.positions[position_id]
        entry_price = position['entry_price']
        quantity = position['quantity']
        
        pnl = (current_price - entry_price) * quantity
        position['pnl'] = pnl
        
        self.daily_pnl += pnl - position.get('last_pnl', 0)
        position['last_pnl'] = pnl
    
    def check_exit_conditions(self, position_id: str, current_price: float) -> Dict[str, any]:
        """Check if position should be exited"""
        
        if position_id not in self.positions:
            return {'should_exit': False, 'reason': 'Position not found'}
        
        position = self.positions[position_id]
        entry_price = position['entry_price']
        stop_loss = position.get('stop_loss')
        target = position.get('target')
        
        if stop_loss and ((current_price <= stop_loss and entry_price > stop_loss) or 
                         (current_price >= stop_loss and entry_price < stop_loss)):
            return {'should_exit': True, 'reason': 'Stop loss hit', 'exit_price': current_price}
        
        if target and ((current_price >= target and entry_price < target) or 
                      (current_price <= target and entry_price > target)):
            return {'should_exit': True, 'reason': 'Target reached', 'exit_price': current_price}
        
        entry_time = position['entry_time']
        if datetime.now().hour >= 15 and datetime.now().minute >= 15:  # 3:15 PM
            return {'should_exit': True, 'reason': 'End of day exit', 'exit_price': current_price}
        
        current_pnl = (current_price - entry_price) * position['quantity']
        max_loss_per_position = entry_price * position['quantity'] * 0.05  # 5% max loss
        
        if current_pnl <= -max_loss_per_position:
            return {'should_exit': True, 'reason': 'Maximum loss per position', 'exit_price': current_price}
        
        return {'should_exit': False, 'reason': 'No exit condition met'}
    
    def close_position(self, position_id: str, exit_price: float, reason: str):
        """Close a position"""
        
        if position_id not in self.positions:
            return
        
        position = self.positions[position_id]
        position['status'] = 'CLOSED'
        position['exit_price'] = exit_price
        position['exit_time'] = datetime.now()
        position['exit_reason'] = reason
        
        final_pnl = (exit_price - position['entry_price']) * position['quantity']
        position['final_pnl'] = final_pnl
        
        self.daily_pnl += final_pnl
        
        self.trade_history.append(position.copy())
        
        del self.positions[position_id]
        
        self.logger.info(f"Position closed: {position_id}, P&L: {final_pnl:.2f}, Reason: {reason}")
        
        if self.daily_pnl >= self.daily_profit_target:
            self.profit_target_reached = True
            self.logger.info(f"🎯 Daily profit target of ₹{self.daily_profit_target} reached! Current P&L: ₹{self.daily_pnl:.2f}")
        
        if self.daily_pnl <= -self.daily_stop_loss:
            self.stop_loss_hit = True
            self.logger.warning(f"🛑 Daily stop loss of ₹{self.daily_stop_loss} hit! Current P&L: ₹{self.daily_pnl:.2f}")
        
        if final_pnl > 0:
            self.winning_trades = getattr(self, 'winning_trades', 0) + 1
        else:
            self.losing_trades = getattr(self, 'losing_trades', 0) + 1
    
    def should_continue_trading(self) -> Dict[str, any]:
        """Check if trading should continue based on profit targets and risk limits"""
        
        continue_trading = True
        reasons = []
        
        if self.profit_target_reached or self.daily_pnl >= self.daily_profit_target:
            continue_trading = False
            reasons.append(f'Daily profit target of ₹{self.daily_profit_target} reached')
        
        if self.stop_loss_hit or self.daily_pnl <= -self.daily_stop_loss:
            continue_trading = False
            reasons.append(f'Daily stop loss of ₹{self.daily_stop_loss} hit (₹{self.daily_pnl:.2f})')
        
        if self.daily_trades >= self.max_daily_trades:
            continue_trading = False
            reasons.append('Daily trade limit reached')
        
        return {
            'continue': continue_trading,
            'current_pnl': self.daily_pnl,
            'target': self.daily_profit_target,
            'stop_loss': self.daily_stop_loss,
            'progress': (self.daily_pnl / self.daily_profit_target * 100) if self.daily_profit_target > 0 else 0,
            'reasons': reasons
        }
    
    def get_daily_summary(self) -> Dict[str, any]:
        """Get daily trading summary"""
        
        open_positions = len(self.positions)
        closed_trades = len([t for t in self.trade_history 
                           if t['exit_time'].date() == datetime.now().date()])
        
        daily_trades_pnl = sum(t['final_pnl'] for t in self.trade_history 
                              if t['exit_time'].date() == datetime.now().date())
        
        return {
            'date': datetime.now().date(),
            'total_trades': self.daily_trades,
            'open_positions': open_positions,
            'closed_trades': closed_trades,
            'daily_pnl': self.daily_pnl,
            'unrealized_pnl': sum(pos['pnl'] for pos in self.positions.values()),
            'total_pnl': self.daily_pnl + sum(pos['pnl'] for pos in self.positions.values()),
            'winning_trades': len([t for t in self.trade_history if t.get('final_pnl', 0) > 0 and t['exit_time'].date() == datetime.now().date()]),
            'losing_trades': len([t for t in self.trade_history if t.get('final_pnl', 0) < 0 and t['exit_time'].date() == datetime.now().date()])
        }
    
    def reset_daily_counters(self):
        """Reset daily counters (call at start of new trading day)"""
        
        self.daily_pnl = 0
        self.daily_trades = 0
        self.profit_target_reached = False
        self.stop_loss_hit = False
        self.winning_trades = 0
        self.losing_trades = 0
        
        yesterday = datetime.now().date() - timedelta(days=1)
        yesterday_trades = [t for t in self.trade_history 
                          if t['exit_time'].date() == yesterday]
        
        if yesterday_trades:
            self.logger.info(f"Archived {len(yesterday_trades)} trades from {yesterday}")
    
    def get_risk_metrics(self) -> Dict[str, any]:
        """Calculate risk metrics"""
        
        if not self.trade_history:
            return {}
        
        pnls = [t['final_pnl'] for t in self.trade_history]
        
        total_trades = len(pnls)
        winning_trades = len([p for p in pnls if p > 0])
        losing_trades = len([p for p in pnls if p < 0])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        avg_win = sum(p for p in pnls if p > 0) / winning_trades if winning_trades > 0 else 0
        avg_loss = sum(p for p in pnls if p < 0) / losing_trades if losing_trades > 0 else 0
        
        profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if avg_loss != 0 and losing_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl': sum(pnls),
            'max_win': max(pnls) if pnls else 0,
            'max_loss': min(pnls) if pnls else 0
        }
