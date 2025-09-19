#!/usr/bin/env python3

"""
Automatic NIFTY Trading Demo with Daily Profit Target
This demonstrates automatic trading focused on NIFTY with ₹1000 daily profit target
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time

from technical_analysis import TechnicalAnalysis
from strategy import TradingStrategy
from risk_manager import RiskManager
from config import Config

def generate_realistic_nifty_data(days: int = 1, intervals_per_day: int = 75) -> pd.DataFrame:
    """Generate realistic NIFTY data for a trading day (9:15 AM - 3:30 PM)"""
    
    base_price = 19500  # Current NIFTY level
    
    today = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)
    end_time = today.replace(hour=15, minute=30)
    
    timestamps = []
    current_time = today
    while current_time <= end_time:
        timestamps.append(current_time)
        current_time += timedelta(minutes=5)
    
    np.random.seed(42)  # For reproducible results
    
    trend_pattern = np.sin(np.linspace(0, np.pi, len(timestamps))) * 0.003
    
    returns = np.random.normal(0, 0.0008, len(timestamps))
    returns += trend_pattern
    
    prices = [base_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    data = []
    for i, (timestamp, price) in enumerate(zip(timestamps, prices)):
        volatility = price * 0.002  # 0.2% volatility
        
        high = price + np.random.uniform(0, volatility)
        low = price - np.random.uniform(0, volatility)
        open_price = prices[i-1] if i > 0 else price
        close = price
        volume = np.random.randint(1000000, 5000000)
        
        data.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': max(open_price, high, close),
            'low': min(open_price, low, close),
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    return df

def simulate_automatic_trading():
    """Simulate automatic NIFTY trading with profit targets"""
    
    print("=" * 70)
    print("AUTOMATIC NIFTY TRADING SIMULATION")
    print("Daily Profit Target: ₹1000")
    print("=" * 70)
    
    config = Config()
    
    strategy = TradingStrategy()
    risk_manager = RiskManager(config)
    
    account_balance = 100000  # ₹1 Lakh
    
    print(f"Account Balance: ₹{account_balance:,.2f}")
    print(f"Daily Profit Target: ₹{config.DAILY_PROFIT_TARGET}")
    print(f"Focus Symbol: {config.FOCUS_SYMBOL}")
    print()
    
    nifty_data = generate_realistic_nifty_data()
    
    trades_executed = []
    analysis_count = 0
    
    for timestamp, row in nifty_data.iterrows():
        analysis_count += 1
        
        trading_status = risk_manager.should_continue_trading()
        
        if not trading_status['continue']:
            print(f"\n🎯 PROFIT TARGET REACHED!")
            print(f"Final P&L: ₹{trading_status['current_pnl']:.2f}")
            print(f"Target: ₹{trading_status['target']:.2f}")
            print(f"Progress: {trading_status['progress']:.1f}%")
            print(f"Total Trades: {len(trades_executed)}")
            break
        
        if analysis_count % 6 != 0:
            continue
        
        print(f"\n⏰ {timestamp.strftime('%H:%M')} - Analyzing NIFTY...")
        print(f"   Current Price: ₹{row['close']:.2f}")
        print(f"   Current P&L: ₹{trading_status['current_pnl']:.2f} / ₹{trading_status['target']:.2f} ({trading_status['progress']:.1f}%)")
        
        recent_data = nifty_data.loc[:timestamp].tail(50)  # Last 50 data points
        
        if len(recent_data) < 30:  # Reduce minimum data requirement
            print("   ⏸️  Insufficient data for analysis")
            continue
        
        signal = strategy.generate_signals('NIFTY', recent_data)
        
        if signal['signal'] != 'NO_SIGNAL':
            print(f"   🎯 Signal: {signal['signal']} | Confidence: {signal['confidence']:.1f}%")
            print(f"   📊 Entry: ₹{signal['entry_price']:.2f} | SL: ₹{signal['stop_loss']:.2f} | Target: ₹{signal['target']:.2f}")
            print(f"   📈 Risk-Reward: {signal['risk_reward_ratio']:.2f}")
            
            risk_check = risk_manager.check_risk_limits(signal, account_balance)
            
            if risk_check['approved'] and risk_check['adjusted_quantity'] > 0:
                trade = {
                    'timestamp': timestamp,
                    'symbol': 'NIFTY',
                    'signal': signal['signal'],
                    'entry_price': signal['entry_price'],
                    'stop_loss': signal['stop_loss'],
                    'target': signal['target'],
                    'quantity': risk_check['adjusted_quantity'],
                    'confidence': signal['confidence']
                }
                
                position_id = risk_manager.add_position({
                    'symbol': signal['symbol'],
                    'entry_price': signal['entry_price'],
                    'quantity': risk_check['adjusted_quantity'],
                    'stop_loss': signal['stop_loss'],
                    'target': signal['target'],
                    'underlying_symbol': 'NSE:NIFTY50-INDEX'
                })
                
                trades_executed.append(trade)
                print(f"   ✅ Trade Executed: {position_id}")
                print(f"   📦 Quantity: {risk_check['adjusted_quantity']} lots")
                
                if np.random.random() < 0.7:  # 70% win rate
                    profit = abs(signal['target'] - signal['entry_price']) * risk_check['adjusted_quantity']
                    risk_manager.close_position(position_id, signal['target'], 'Target hit')
                    print(f"   💰 Position closed at target: +₹{profit:.2f}")
                else:
                    loss = abs(signal['entry_price'] - signal['stop_loss']) * risk_check['adjusted_quantity']
                    risk_manager.close_position(position_id, signal['stop_loss'], 'Stop loss hit')
                    print(f"   📉 Position closed at stop loss: -₹{loss:.2f}")
                
            else:
                print(f"   ❌ Trade rejected: {', '.join(risk_check['reasons'])}")
        else:
            print("   ⏸️  No signal - market conditions not suitable")
    
    print("\n" + "=" * 70)
    print("TRADING SESSION SUMMARY")
    print("=" * 70)
    
    final_status = risk_manager.should_continue_trading()
    summary = risk_manager.get_daily_summary()
    
    print(f"Total Trades Executed: {len(trades_executed)}")
    print(f"Final P&L: ₹{final_status['current_pnl']:.2f}")
    print(f"Target Achievement: {final_status['progress']:.1f}%")
    print(f"Win Rate: {(summary.get('winning_trades', 0) / max(summary.get('total_trades', 1), 1)) * 100:.1f}%")
    
    if final_status['current_pnl'] >= config.DAILY_PROFIT_TARGET:
        print("🎉 DAILY PROFIT TARGET ACHIEVED!")
    elif final_status['current_pnl'] > 0:
        print("📈 Profitable day, but target not reached")
    else:
        print("📉 Loss day - risk management protected capital")
    
    print("\n💡 This simulation shows how the robot would:")
    print("   • Focus exclusively on NIFTY trading")
    print("   • Monitor profit targets in real-time")
    print("   • Stop trading once ₹1000 daily target is reached")
    print("   • Apply strict risk management rules")
    print("   • Execute trades automatically based on technical signals")

def main():
    """Run automatic NIFTY trading demo"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        simulate_automatic_trading()
        
        print("\n" + "=" * 70)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nTo enable automatic NIFTY trading:")
        print("1. Set up your Fyers API credentials in .env file")
        print("2. Run: python main.py --symbol NIFTY")
        print("3. Monitor the robot as it works towards ₹1000 daily profit")
        print("\n⚠️  IMPORTANT: Always test with small amounts first!")
        
    except Exception as e:
        print(f"Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
