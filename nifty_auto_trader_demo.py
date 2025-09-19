#!/usr/bin/env python3

"""
Enhanced NIFTY Auto Trading Demo with ₹1000 Daily Profit Target
This demonstrates the complete automatic trading workflow with realistic scenarios
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

def create_trending_nifty_data() -> pd.DataFrame:
    """Create realistic NIFTY data with strong trends for signal generation"""
    
    base_price = 19500
    periods = 75  # Full trading day (9:15 AM - 3:30 PM in 5-min intervals)
    
    start_time = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)
    timestamps = [start_time + timedelta(minutes=5*i) for i in range(periods)]
    
    np.random.seed(123)  # Different seed for better signals
    
    phase1_returns = np.random.normal(0, 0.001, 20)
    
    phase2_trend = np.linspace(0, 0.025, 25)  # 2.5% upward trend
    phase2_returns = np.random.normal(0.001, 0.0015, 25) + phase2_trend * 0.1
    
    phase3_trend = np.linspace(0, -0.015, 20)  # 1.5% downward trend
    phase3_returns = np.random.normal(-0.0005, 0.0012, 20) + phase3_trend * 0.1
    
    phase4_returns = np.random.normal(0.0008, 0.001, 10)
    
    all_returns = np.concatenate([phase1_returns, phase2_returns, phase3_returns, phase4_returns])
    
    prices = [base_price]
    for ret in all_returns:
        prices.append(prices[-1] * (1 + ret))
    
    data = []
    for i, (timestamp, price) in enumerate(zip(timestamps, prices)):
        volatility = price * 0.0015
        
        high = price + np.random.uniform(0, volatility)
        low = price - np.random.uniform(0, volatility)
        open_price = prices[i-1] if i > 0 else price
        close = price
        volume = np.random.randint(2000000, 8000000)
        
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

def simulate_auto_nifty_trading():
    """Simulate automatic NIFTY trading with ₹1000 profit target"""
    
    print("=" * 80)
    print("🚀 AUTOMATIC NIFTY TRADING ROBOT - LIVE SIMULATION")
    print("Target: ₹1000 Daily Profit | Focus: NIFTY Only")
    print("=" * 80)
    
    config = Config()
    strategy = TradingStrategy()
    risk_manager = RiskManager(config)
    
    account_balance = 100000  # ₹1 Lakh
    
    print(f"💰 Account Balance: ₹{account_balance:,.2f}")
    print(f"🎯 Daily Profit Target: ₹{config.DAILY_PROFIT_TARGET}")
    print(f"📊 Focus Symbol: NIFTY")
    print(f"⚡ Auto Trading: ENABLED")
    print()
    
    nifty_data = create_trending_nifty_data()
    
    trades_executed = []
    analysis_count = 0
    
    print("🔄 Starting automatic trading session...")
    print("-" * 80)
    
    for timestamp, row in nifty_data.iterrows():
        analysis_count += 1
        
        trading_status = risk_manager.should_continue_trading()
        
        if not trading_status['continue']:
            print(f"\n🎉 PROFIT TARGET ACHIEVED!")
            print(f"💰 Final P&L: ₹{trading_status['current_pnl']:.2f}")
            print(f"🎯 Target: ₹{trading_status['target']:.2f}")
            print(f"📈 Achievement: {trading_status['progress']:.1f}%")
            print(f"🛑 Stopping Reason: {', '.join(trading_status['reasons'])}")
            break
        
        if analysis_count % 4 != 0:
            continue
        
        current_time = timestamp.strftime('%H:%M')
        current_price = row['close']
        
        print(f"\n⏰ {current_time} | NIFTY: ₹{current_price:.2f} | P&L: ₹{trading_status['current_pnl']:.2f} ({trading_status['progress']:.1f}%)")
        
        recent_data = nifty_data.loc[:timestamp].tail(40)
        
        if len(recent_data) < 25:
            print("   ⏸️  Building data history...")
            continue
        
        signal = strategy.generate_signals('NIFTY', recent_data)
        
        if signal['signal'] != 'NO_SIGNAL':
            print(f"   🎯 SIGNAL: {signal['signal']} | Confidence: {signal['confidence']:.1f}% | R:R: {signal['risk_reward_ratio']:.2f}")
            print(f"   💹 Entry: ₹{signal['entry_price']:.2f} | SL: ₹{signal['stop_loss']:.2f} | Target: ₹{signal['target']:.2f}")
            
            risk_check = risk_manager.check_risk_limits(signal, account_balance)
            
            if risk_check['approved'] and risk_check['adjusted_quantity'] > 0:
                trade = {
                    'timestamp': timestamp,
                    'signal': signal['signal'],
                    'entry_price': signal['entry_price'],
                    'stop_loss': signal['stop_loss'],
                    'target': signal['target'],
                    'quantity': risk_check['adjusted_quantity'],
                    'confidence': signal['confidence']
                }
                
                position_id = risk_manager.add_position({
                    'symbol': 'NIFTY',
                    'entry_price': signal['entry_price'],
                    'quantity': risk_check['adjusted_quantity'],
                    'stop_loss': signal['stop_loss'],
                    'target': signal['target'],
                    'underlying_symbol': 'NSE:NIFTY50-INDEX'
                })
                
                trades_executed.append(trade)
                print(f"   ✅ TRADE EXECUTED: {position_id}")
                print(f"   📦 Quantity: {risk_check['adjusted_quantity']} lots")
                
                win_probability = 0.65 if signal['confidence'] > 70 else 0.55
                
                if np.random.random() < win_probability:
                    profit = abs(signal['target'] - signal['entry_price']) * risk_check['adjusted_quantity']
                    risk_manager.close_position(position_id, signal['target'], 'Target achieved')
                    print(f"   💰 PROFIT: +₹{profit:.2f} (Target hit)")
                else:
                    loss = abs(signal['entry_price'] - signal['stop_loss']) * risk_check['adjusted_quantity']
                    risk_manager.close_position(position_id, signal['stop_loss'], 'Stop loss hit')
                    print(f"   📉 LOSS: -₹{loss:.2f} (Stop loss hit)")
                
                updated_status = risk_manager.should_continue_trading()
                print(f"   📊 Updated P&L: ₹{updated_status['current_pnl']:.2f} | Progress: {updated_status['progress']:.1f}%")
                
            else:
                print(f"   ❌ TRADE REJECTED: {', '.join(risk_check['reasons'])}")
        else:
            print("   ⏸️  No signal - waiting for better conditions")
    
    print("\n" + "=" * 80)
    print("📊 TRADING SESSION COMPLETED")
    print("=" * 80)
    
    final_status = risk_manager.should_continue_trading()
    summary = risk_manager.get_daily_summary()
    
    print(f"🕐 Session Duration: Full trading day")
    print(f"📈 Total Trades: {len(trades_executed)}")
    print(f"💰 Final P&L: ₹{final_status['current_pnl']:.2f}")
    print(f"🎯 Target: ₹{final_status['target']:.2f}")
    print(f"📊 Achievement: {final_status['progress']:.1f}%")
    
    if summary.get('winning_trades', 0) > 0 or summary.get('losing_trades', 0) > 0:
        total_trades = summary.get('winning_trades', 0) + summary.get('losing_trades', 0)
        win_rate = (summary.get('winning_trades', 0) / max(total_trades, 1)) * 100
        print(f"🏆 Win Rate: {win_rate:.1f}%")
    
    print()
    if final_status['current_pnl'] >= config.DAILY_PROFIT_TARGET:
        print("🎉 SUCCESS: Daily profit target achieved!")
        print("🛑 Robot automatically stopped trading to preserve profits")
    elif final_status['current_pnl'] > 0:
        print("📈 POSITIVE: Profitable session, target partially achieved")
    else:
        print("🛡️  PROTECTED: Risk management prevented larger losses")
    
    print("\n💡 Key Features Demonstrated:")
    print("   ✅ Automatic NIFTY-only trading")
    print("   ✅ Real-time profit target monitoring")
    print("   ✅ Automatic stop when ₹1000 target reached")
    print("   ✅ Risk management and position sizing")
    print("   ✅ Technical analysis-based signals")
    print("   ✅ Stop loss and target management")
    
    return final_status['current_pnl'] >= config.DAILY_PROFIT_TARGET

def main():
    """Run the enhanced automatic NIFTY trading demo"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        success = simulate_auto_nifty_trading()
        
        print("\n" + "=" * 80)
        print("🚀 DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        if success:
            print("✅ Profit target demonstration: SUCCESSFUL")
        else:
            print("📊 Risk management demonstration: SUCCESSFUL")
        
        print("\n🔧 To enable live automatic NIFTY trading:")
        print("1. Configure Fyers API credentials in .env file")
        print("2. Run: python main.py --symbol NIFTY")
        print("3. Monitor as robot works towards ₹1000 daily profit")
        print("\n⚠️  CRITICAL: Always start with paper trading first!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
