#!/usr/bin/env python3

import sys
import time
import schedule
from datetime import datetime, timedelta
import logging
from typing import Dict, List

from config import Config
from fyers_client import FyersClient
from technical_analysis import TechnicalAnalysis
from strategy import TradingStrategy
from enhanced_strategy import EnhancedTradingStrategy
from risk_manager import RiskManager

class TradingRobot:
    def __init__(self):
        self.config = Config()
        self.fyers_client = FyersClient()
        self.enhanced_mode = getattr(self.config, 'ENHANCED_MODE', False)
        if self.enhanced_mode:
            self.strategy = EnhancedTradingStrategy()
        else:
            self.strategy = TradingStrategy()
        self.risk_manager = RiskManager(self.config)
        self.logger = self._setup_logger()
        
        self.is_market_open = False
        self.account_balance = 100000  # Default balance, should be fetched from API
        
        self.last_analysis_time = None
        self.analysis_interval = 300  # 5 minutes
        
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
    
    def initialize(self) -> bool:
        """Initialize the trading robot"""
        
        self.logger.info("Initializing Trading Robot...")
        
        if not self.fyers_client.client:
            self.logger.error("Failed to initialize Fyers client")
            return False
        
        try:
            funds = self.fyers_client.get_funds()
            if funds:
                for fund in funds:
                    if fund['title'] == 'Total Balance':
                        self.account_balance = fund['equityAmount']
                        break
                
                self.logger.info(f"Account balance: ₹{self.account_balance:,.2f}")
            else:
                self.logger.warning("Could not fetch account balance, using default")
        
        except Exception as e:
            self.logger.error(f"Error fetching account balance: {str(e)}")
        
        self._schedule_tasks()
        
        self.logger.info("Trading Robot initialized successfully")
        return True
    
    def _schedule_tasks(self):
        """Schedule trading tasks"""
        
        schedule.every(5).minutes.do(self._run_analysis)
        
        schedule.every().day.at("09:15").do(self._daily_reset)
        
        schedule.every().day.at("15:30").do(self._end_of_day_cleanup)
        
        schedule.every(1).minutes.do(self._monitor_positions)
    
    def _is_market_open(self) -> bool:
        """Check if market is open"""
        
        now = datetime.now()
        
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def _daily_reset(self):
        """Reset daily counters and prepare for new trading day"""
        
        self.logger.info("Starting new trading day - resetting counters")
        self.risk_manager.reset_daily_counters()
        
        summary = self.risk_manager.get_daily_summary()
        self.logger.info(f"Previous day summary: {summary}")
    
    def _run_analysis(self):
        """Run market analysis and generate signals"""
        
        if not self._is_market_open():
            return
        
        self.logger.info("Running market analysis...")
        
        try:
            signals = []
            
            for symbol_name, symbol in self.config.SYMBOLS.items():
                self.logger.info(f"Analyzing {symbol_name} ({symbol})")
                
                data = self.fyers_client.get_historical_data(
                    symbol=symbol,
                    resolution="5",  # 5-minute candles
                    range_from=(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                    range_to=datetime.now().strftime("%Y-%m-%d")
                )
                
                if data is None or len(data) < 50:
                    self.logger.warning(f"Insufficient data for {symbol_name}")
                    continue
                
                signal = self.strategy.generate_signals(symbol, data)
                
                if signal['signal'] != 'NO_SIGNAL':
                    signals.append(signal)
                    self.logger.info(f"Signal generated for {symbol_name}: {signal['signal']} (Confidence: {signal['confidence']}%)")
            
            filtered_signals = self.strategy.filter_signals(signals)
            
            recommendations = self.strategy.get_option_recommendations(filtered_signals)
            
            for recommendation in recommendations:
                self._execute_trade(recommendation)
        
        except Exception as e:
            self.logger.error(f"Error in market analysis: {str(e)}")
    
    def _execute_trade(self, recommendation: Dict):
        """Execute a trade based on recommendation"""
        
        try:
            risk_check = self.risk_manager.check_risk_limits(recommendation, self.account_balance)
            
            if not risk_check['approved']:
                self.logger.info(f"Trade rejected: {', '.join(risk_check['reasons'])}")
                return
            
            recommendation['quantity'] = risk_check['adjusted_quantity']
            
            if recommendation['quantity'] == 0:
                self.logger.info("Trade rejected: Zero quantity after risk adjustment")
                return
            
            
            self.logger.info("=" * 50)
            self.logger.info("TRADE RECOMMENDATION")
            self.logger.info("=" * 50)
            self.logger.info(f"Symbol: {recommendation['option_symbol']}")
            self.logger.info(f"Action: {recommendation['action']}")
            self.logger.info(f"Quantity: {recommendation['quantity']}")
            self.logger.info(f"Strike: {recommendation['strike_price']}")
            self.logger.info(f"Type: {recommendation['option_type']}")
            self.logger.info(f"Confidence: {recommendation['confidence']}%")
            self.logger.info(f"Stop Loss: {recommendation['stop_loss']:.2f}")
            self.logger.info(f"Target: {recommendation['target']:.2f}")
            self.logger.info(f"Risk-Reward: {recommendation['risk_reward_ratio']:.2f}")
            self.logger.info(f"Reasons: {', '.join(recommendation['reasons'])}")
            self.logger.info("=" * 50)
            
            position_id = self.risk_manager.add_position(recommendation)
            
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")
    
    def _monitor_positions(self):
        """Monitor open positions for exit conditions"""
        
        if not self._is_market_open():
            return
        
        try:
            for position_id, position in list(self.risk_manager.positions.items()):
                symbol = position['symbol']
                
                quotes = self.fyers_client.get_quotes([symbol])
                if not quotes:
                    continue
                
                current_price = quotes[symbol]['lp']  # Last price
                
                self.risk_manager.update_position_pnl(position_id, current_price)
                
                exit_check = self.risk_manager.check_exit_conditions(position_id, current_price)
                
                if exit_check['should_exit']:
                    self.logger.info(f"Exiting position {position_id}: {exit_check['reason']}")
                    
                    
                    self.risk_manager.close_position(
                        position_id, 
                        exit_check['exit_price'], 
                        exit_check['reason']
                    )
        
        except Exception as e:
            self.logger.error(f"Error monitoring positions: {str(e)}")
    
    def _end_of_day_cleanup(self):
        """End of day cleanup and reporting"""
        
        self.logger.info("End of day cleanup...")
        
        for position_id in list(self.risk_manager.positions.keys()):
            position = self.risk_manager.positions[position_id]
            symbol = position['symbol']
            
            try:
                quotes = self.fyers_client.get_quotes([symbol])
                if quotes:
                    current_price = quotes[symbol]['lp']
                    self.risk_manager.close_position(position_id, current_price, "End of day")
            except:
                self.risk_manager.close_position(position_id, position['entry_price'], "End of day - no price")
        
        summary = self.risk_manager.get_daily_summary()
        risk_metrics = self.risk_manager.get_risk_metrics()
        
        self.logger.info("=" * 50)
        self.logger.info("DAILY TRADING SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Date: {summary['date']}")
        self.logger.info(f"Total Trades: {summary['total_trades']}")
        self.logger.info(f"Closed Trades: {summary['closed_trades']}")
        self.logger.info(f"Daily P&L: ₹{summary['total_pnl']:.2f}")
        
        if risk_metrics:
            self.logger.info(f"Win Rate: {risk_metrics['win_rate']:.1%}")
            self.logger.info(f"Profit Factor: {risk_metrics['profit_factor']:.2f}")
            self.logger.info(f"Total P&L: ₹{risk_metrics['total_pnl']:.2f}")
        
        self.logger.info("=" * 50)
    
    def run(self):
        """Main trading loop"""
        
        if not self.initialize():
            self.logger.error("Failed to initialize trading robot")
            return
        
        self.logger.info("Trading Robot started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("Trading Robot stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
        finally:
            self._shutdown()
    
    def _shutdown(self):
        """Shutdown procedures"""
        
        self.logger.info("Shutting down Trading Robot...")
        
        summary = self.risk_manager.get_daily_summary()
        self.logger.info(f"Final summary: {summary}")
        
        self.logger.info("Trading Robot shutdown complete")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fyers Trading Robot')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode (no actual trades)')
    parser.add_argument('--enhanced', action='store_true', help='Use enhanced high-probability strategy')
    parser.add_argument('--symbol', type=str, choices=['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'ALL'], 
                       default='ALL', help='Symbol to trade')
    
    args = parser.parse_args()
    
    config = Config()
    if args.enhanced:
        config.ENHANCED_MODE = True
        print("🚀 Enhanced high-probability trading mode enabled")
        print(f"🎯 Daily profit target: ₹{config.DAILY_PROFIT_TARGET}")
        print(f"🛑 Daily stop loss: ₹{config.DAILY_STOP_LOSS}")
    
    if args.demo:
        print("Running in DEMO mode - no actual trades will be placed")
    
    robot = TradingRobot()
    robot.run()

if __name__ == "__main__":
    main()
