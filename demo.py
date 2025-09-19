#!/usr/bin/env python3

"""
Demo script to test the trading robot with sample data
This script demonstrates the functionality without requiring actual API credentials
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from technical_analysis import TechnicalAnalysis
from strategy import TradingStrategy
from risk_manager import RiskManager
from config import Config

def generate_sample_data(symbol: str, days: int = 30) -> pd.DataFrame:
    """Generate sample OHLCV data for testing"""
    
    base_prices = {
        'NIFTY': 19500,
        'BANKNIFTY': 44000,
        'FINNIFTY': 19800
    }
    
    base_price = base_prices.get(symbol, 19500)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='5min')  # 5-minute intervals
    
    np.random.seed(42)  # For reproducible results
    
    returns = np.random.normal(0, 0.002, len(dates))  # 0.2% volatility
    
    trend = np.linspace(0, 0.05, len(dates))  # 5% upward trend over period
    returns += trend / len(dates)
    
    prices = [base_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        volatility = price * 0.001  # 0.1% volatility
        
        high = price + np.random.uniform(0, volatility)
        low = price - np.random.uniform(0, volatility)
        open_price = price + np.random.uniform(-volatility/2, volatility/2)
        close = price
        volume = np.random.randint(100000, 1000000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': max(open_price, high, close),
            'low': min(open_price, low, close),
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    return df

def demo_technical_analysis():
    """Demonstrate technical analysis functionality"""
    
    print("=" * 60)
    print("TECHNICAL ANALYSIS DEMO")
    print("=" * 60)
    
    ta = TechnicalAnalysis()
    
    data = generate_sample_data('NIFTY', 30)
    print(f"Generated {len(data)} data points for NIFTY")
    
    close_prices = data['close']
    
    ema_9 = ta.calculate_ema(close_prices, 9)
    ema_21 = ta.calculate_ema(close_prices, 21)
    rsi = ta.calculate_rsi(close_prices)
    macd = ta.calculate_macd(close_prices)
    bollinger = ta.calculate_bollinger_bands(close_prices)
    
    print(f"\nLatest Technical Indicators:")
    print(f"Current Price: ₹{close_prices.iloc[-1]:.2f}")
    print(f"EMA 9: ₹{ema_9.iloc[-1]:.2f}")
    print(f"EMA 21: ₹{ema_21.iloc[-1]:.2f}")
    print(f"RSI: {rsi.iloc[-1]:.2f}")
    print(f"MACD: {macd['macd'].iloc[-1]:.2f}")
    print(f"MACD Signal: {macd['signal'].iloc[-1]:.2f}")
    print(f"Bollinger Upper: ₹{bollinger['upper'].iloc[-1]:.2f}")
    print(f"Bollinger Lower: ₹{bollinger['lower'].iloc[-1]:.2f}")
    
    trend_analysis = ta.analyze_trend(data)
    print(f"\nTrend Analysis:")
    print(f"Trend: {trend_analysis['trend']}")
    print(f"Signal Strength: {trend_analysis['signal_strength']}")
    
    high_low_analysis = ta.get_high_low_analysis(data)
    print(f"\nHigh/Low Analysis:")
    print(f"Current High: ₹{high_low_analysis['current_high']:.2f}")
    print(f"Current Low: ₹{high_low_analysis['current_low']:.2f}")
    print(f"Previous High: ₹{high_low_analysis['prev_high']:.2f}")
    print(f"Previous Low: ₹{high_low_analysis['prev_low']:.2f}")
    print(f"High Breakout: {high_low_analysis['high_breakout']}")
    print(f"Low Breakdown: {high_low_analysis['low_breakdown']}")

def demo_strategy():
    """Demonstrate strategy signal generation"""
    
    print("\n" + "=" * 60)
    print("STRATEGY DEMO")
    print("=" * 60)
    
    strategy = TradingStrategy()
    
    symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']
    all_signals = []
    
    for symbol in symbols:
        print(f"\nAnalyzing {symbol}...")
        
        data = generate_sample_data(symbol, 30)
        
        signal = strategy.generate_signals(symbol, data)
        all_signals.append(signal)
        
        print(f"Signal: {signal['signal']}")
        print(f"Confidence: {signal['confidence']:.1f}%")
        print(f"Current Price: ₹{signal['current_price']:.2f}")
        
        if signal['signal'] != 'NO_SIGNAL':
            print(f"Stop Loss: ₹{signal['stop_loss']:.2f}")
            print(f"Target: ₹{signal['target']:.2f}")
            print(f"Risk-Reward Ratio: {signal['risk_reward_ratio']:.2f}")
            print(f"Reasons: {', '.join(signal['reasons'])}")
    
    filtered_signals = strategy.filter_signals(all_signals)
    print(f"\nFiltered Signals: {len(filtered_signals)} out of {len(all_signals)}")
    
    recommendations = strategy.get_option_recommendations(filtered_signals)
    
    print(f"\nOption Recommendations:")
    for rec in recommendations:
        print(f"- {rec['option_symbol']}: {rec['action']} {rec['quantity']} lots")
        print(f"  Strike: {rec['strike_price']}, Type: {rec['option_type']}")
        print(f"  Confidence: {rec['confidence']:.1f}%")

def demo_risk_management():
    """Demonstrate risk management functionality"""
    
    print("\n" + "=" * 60)
    print("RISK MANAGEMENT DEMO")
    print("=" * 60)
    
    config = Config()
    risk_manager = RiskManager(config)
    
    account_balance = 100000  # ₹1 Lakh
    
    sample_signal = {
        'symbol': 'NSE:NIFTY50-INDEX',
        'entry_price': 19500,
        'stop_loss': 19200,
        'target': 19800,
        'quantity': 100,
        'underlying_symbol': 'NSE:NIFTY50-INDEX'
    }
    
    risk_check = risk_manager.check_risk_limits(sample_signal, account_balance)
    
    print(f"Risk Check Results:")
    print(f"Approved: {risk_check['approved']}")
    print(f"Original Quantity: {sample_signal['quantity']}")
    print(f"Adjusted Quantity: {risk_check['adjusted_quantity']}")
    print(f"Reasons: {', '.join(risk_check['reasons'])}")
    
    if risk_check['approved']:
        position_id = risk_manager.add_position(sample_signal)
        print(f"\nPosition Added: {position_id}")
        
        test_prices = [19450, 19400, 19350, 19300, 19250, 19200]  # Declining prices
        
        for price in test_prices:
            risk_manager.update_position_pnl(position_id, price)
            exit_check = risk_manager.check_exit_conditions(position_id, price)
            
            print(f"Price: ₹{price}, Should Exit: {exit_check['should_exit']}")
            if exit_check['should_exit']:
                print(f"Exit Reason: {exit_check['reason']}")
                risk_manager.close_position(position_id, price, exit_check['reason'])
                break
    
    risk_metrics = risk_manager.get_risk_metrics()
    if risk_metrics:
        print(f"\nRisk Metrics:")
        for key, value in risk_metrics.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")

def demo_full_workflow():
    """Demonstrate the complete trading workflow"""
    
    print("\n" + "=" * 60)
    print("FULL WORKFLOW DEMO")
    print("=" * 60)
    
    config = Config()
    strategy = TradingStrategy()
    risk_manager = RiskManager(config)
    
    account_balance = 100000
    
    print(f"Account Balance: ₹{account_balance:,.2f}")
    print(f"Max Risk Per Trade: {config.MAX_RISK_PER_TRADE:.1%}")
    print(f"Max Daily Loss: {config.MAX_DAILY_LOSS:.1%}")
    
    symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']
    
    for symbol in symbols:
        print(f"\n--- Analyzing {symbol} ---")
        
        data = generate_sample_data(symbol, 30)
        signal = strategy.generate_signals(symbol, data)
        
        if signal['signal'] == 'NO_SIGNAL':
            print(f"No signal generated for {symbol}")
            continue
        
        print(f"Signal: {signal['signal']} (Confidence: {signal['confidence']:.1f}%)")
        
        filtered_signals = strategy.filter_signals([signal])
        
        if not filtered_signals:
            print(f"Signal filtered out for {symbol}")
            continue
        
        recommendations = strategy.get_option_recommendations(filtered_signals)
        
        for rec in recommendations:
            print(f"Recommendation: {rec['action']} {rec['option_symbol']}")
            
            risk_check = risk_manager.check_risk_limits(rec, account_balance)
            
            if risk_check['approved']:
                print(f"✓ Trade approved - Quantity: {risk_check['adjusted_quantity']}")
                
                rec['quantity'] = risk_check['adjusted_quantity']
                position_id = risk_manager.add_position(rec)
                print(f"Position added: {position_id}")
                
            else:
                print(f"✗ Trade rejected: {', '.join(risk_check['reasons'])}")
    
    summary = risk_manager.get_daily_summary()
    print(f"\nDaily Summary:")
    print(f"Total Trades: {summary['total_trades']}")
    print(f"Open Positions: {summary['open_positions']}")

def main():
    """Run all demos"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("TRADING ROBOT DEMO")
    print("This demo shows the functionality without requiring API credentials")
    print("All data is simulated for demonstration purposes")
    
    try:
        demo_technical_analysis()
        demo_strategy()
        demo_risk_management()
        demo_full_workflow()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nTo run with real data:")
        print("1. Set up your Fyers API credentials in .env file")
        print("2. Run: python main.py --demo")
        print("3. For live trading: python main.py")
        
    except Exception as e:
        print(f"Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
