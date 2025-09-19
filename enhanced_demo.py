#!/usr/bin/env python3

"""
Enhanced demo script that generates more realistic trading signals
This demonstrates the full functionality with better signal generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from technical_analysis import TechnicalAnalysis
from strategy import TradingStrategy
from risk_manager import RiskManager
from config import Config

def generate_trending_data(symbol: str, days: int = 30, trend_direction: str = 'bullish') -> pd.DataFrame:
    """Generate sample data with specific trend patterns for better signal generation"""
    
    base_prices = {
        'NIFTY': 19500,
        'BANKNIFTY': 44000,
        'FINNIFTY': 19800
    }
    
    base_price = base_prices.get(symbol, 19500)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='5min')
    
    np.random.seed(hash(symbol) % 1000)  # Different seed for each symbol
    
    if trend_direction == 'bullish':
        base_returns = np.random.normal(0.00005, 0.0008, len(dates))  # Small positive bias
        trend_component = np.linspace(0, 0.005, len(dates))  # 0.5% upward trend
    elif trend_direction == 'bearish':
        base_returns = np.random.normal(-0.00005, 0.0008, len(dates))  # Small negative bias
        trend_component = np.linspace(0, -0.005, len(dates))  # 0.5% downward trend
    else:
        base_returns = np.random.normal(0, 0.0006, len(dates))
        trend_component = np.sin(np.linspace(0, 4*np.pi, len(dates))) * 0.002
    
    returns = base_returns + trend_component / len(dates)
    
    for i in range(50, len(returns), 100):
        if trend_direction == 'bullish':
            returns[i:i+20] += 0.0002  # Small momentum bursts
        elif trend_direction == 'bearish':
            returns[i:i+20] -= 0.0002
    
    prices = [base_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        volatility = price * 0.002  # 0.2% volatility
        
        high = price + np.random.uniform(0, volatility)
        low = price - np.random.uniform(0, volatility)
        open_price = price + np.random.uniform(-volatility/2, volatility/2)
        close = price
        volume = np.random.randint(500000, 2000000)
        
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

def demo_signal_generation():
    """Demonstrate signal generation with different market conditions"""
    
    print("=" * 70)
    print("ENHANCED SIGNAL GENERATION DEMO")
    print("=" * 70)
    
    strategy = TradingStrategy()
    
    market_conditions = {
        'NIFTY': 'bullish',
        'BANKNIFTY': 'bearish', 
        'FINNIFTY': 'neutral'
    }
    
    all_signals = []
    
    for symbol, condition in market_conditions.items():
        print(f"\n--- {symbol} ({condition.upper()} MARKET) ---")
        
        data = generate_trending_data(symbol, 30, condition)
        
        signal = strategy.generate_signals(symbol, data)
        all_signals.append(signal)
        
        print(f"Signal: {signal['signal']}")
        print(f"Confidence: {signal['confidence']:.1f}%")
        print(f"Current Price: ₹{signal['current_price']:.2f}")
        print(f"Trend: {signal['trend']}")
        print(f"RSI: {signal['rsi']:.2f}")
        
        if signal['signal'] != 'NO_SIGNAL':
            print(f"Entry Price: ₹{signal['entry_price']:.2f}")
            print(f"Stop Loss: ₹{signal['stop_loss']:.2f}")
            print(f"Target: ₹{signal['target']:.2f}")
            print(f"Risk-Reward Ratio: {signal['risk_reward_ratio']:.2f}")
            print(f"Reasons: {', '.join(signal['reasons'])}")
        else:
            print("No signal generated - market conditions don't meet criteria")
    
    filtered_signals = strategy.filter_signals(all_signals)
    print(f"\n--- SIGNAL FILTERING ---")
    print(f"Original signals: {len(all_signals)}")
    print(f"Filtered signals: {len(filtered_signals)}")
    
    recommendations = strategy.get_option_recommendations(filtered_signals)
    
    print(f"\n--- OPTION RECOMMENDATIONS ---")
    for i, rec in enumerate(recommendations, 1):
        print(f"\nRecommendation {i}:")
        print(f"  Underlying: {rec['underlying_symbol']}")
        print(f"  Option: {rec['option_symbol']}")
        print(f"  Action: {rec['action']} {rec['quantity']} lots")
        print(f"  Strike: {rec['strike_price']} {rec['option_type']}")
        print(f"  Confidence: {rec['confidence']:.1f}%")
        print(f"  Risk-Reward: {rec['risk_reward_ratio']:.2f}")
        print(f"  Reasons: {', '.join(rec['reasons'])}")

def demo_comprehensive_risk_management():
    """Demonstrate comprehensive risk management scenarios"""
    
    print("\n" + "=" * 70)
    print("COMPREHENSIVE RISK MANAGEMENT DEMO")
    print("=" * 70)
    
    config = Config()
    risk_manager = RiskManager(config)
    
    account_balance = 500000  # ₹5 Lakh
    
    print(f"Account Balance: ₹{account_balance:,.2f}")
    print(f"Max Risk Per Trade: {config.MAX_RISK_PER_TRADE:.1%}")
    print(f"Max Daily Loss: {config.MAX_DAILY_LOSS:.1%}")
    
    test_trades = [
        {
            'symbol': 'NSE:NIFTY50-INDEX',
            'entry_price': 19500,
            'stop_loss': 19200,
            'target': 19950,
            'quantity': 200,
            'underlying_symbol': 'NSE:NIFTY50-INDEX'
        },
        {
            'symbol': 'NSE:NIFTYBANK-INDEX',
            'entry_price': 44000,
            'stop_loss': 43500,
            'target': 44800,
            'quantity': 100,
            'underlying_symbol': 'NSE:NIFTYBANK-INDEX'
        },
        {
            'symbol': 'NSE:FINNIFTY-INDEX',
            'entry_price': 19800,
            'stop_loss': 19600,
            'target': 20100,
            'quantity': 150,
            'underlying_symbol': 'NSE:FINNIFTY-INDEX'
        }
    ]
    
    approved_trades = []
    
    for i, trade in enumerate(test_trades, 1):
        print(f"\n--- TRADE {i}: {trade['symbol'].split(':')[1]} ---")
        
        risk_check = risk_manager.check_risk_limits(trade, account_balance)
        
        print(f"Original Quantity: {trade['quantity']}")
        print(f"Adjusted Quantity: {risk_check['adjusted_quantity']}")
        print(f"Approved: {risk_check['approved']}")
        print(f"Reasons: {', '.join(risk_check['reasons'])}")
        
        if risk_check['approved']:
            trade['quantity'] = risk_check['adjusted_quantity']
            position_id = risk_manager.add_position(trade)
            approved_trades.append((position_id, trade))
            print(f"✓ Position added: {position_id}")
        else:
            print("✗ Trade rejected")
    
    print(f"\n--- POSITION MONITORING SIMULATION ---")
    
    price_scenarios = [
        {'NIFTY': 19450, 'BANKNIFTY': 43800, 'FINNIFTY': 19750},  # Small move
        {'NIFTY': 19300, 'BANKNIFTY': 43600, 'FINNIFTY': 19650},  # Larger move
        {'NIFTY': 19150, 'BANKNIFTY': 43400, 'FINNIFTY': 19550},  # Near stop loss
        {'NIFTY': 19100, 'BANKNIFTY': 43300, 'FINNIFTY': 19500},  # Stop loss hit
    ]
    
    for scenario_num, prices in enumerate(price_scenarios, 1):
        print(f"\nScenario {scenario_num}: Market moves to {prices}")
        
        for position_id, trade in approved_trades.copy():
            if position_id not in risk_manager.positions:
                continue  # Position already closed
            
            symbol_name = trade['symbol'].split(':')[1].replace('50-INDEX', '').replace('BANK-INDEX', 'BANK').replace('-INDEX', '')
            current_price = prices.get(symbol_name, trade['entry_price'])
            
            risk_manager.update_position_pnl(position_id, current_price)
            
            exit_check = risk_manager.check_exit_conditions(position_id, current_price)
            
            position = risk_manager.positions[position_id]
            print(f"  {symbol_name}: Price ₹{current_price:.0f}, P&L: ₹{position['pnl']:.2f}")
            
            if exit_check['should_exit']:
                print(f"    → EXIT: {exit_check['reason']}")
                risk_manager.close_position(position_id, current_price, exit_check['reason'])
                approved_trades = [(pid, t) for pid, t in approved_trades if pid != position_id]
    
    summary = risk_manager.get_daily_summary()
    risk_metrics = risk_manager.get_risk_metrics()
    
    print(f"\n--- FINAL SUMMARY ---")
    print(f"Total Trades: {summary['total_trades']}")
    print(f"Open Positions: {summary['open_positions']}")
    print(f"Closed Trades: {summary['closed_trades']}")
    print(f"Total P&L: ₹{summary['total_pnl']:.2f}")
    
    if risk_metrics:
        print(f"Win Rate: {risk_metrics['win_rate']:.1%}")
        print(f"Average Win: ₹{risk_metrics['avg_win']:.2f}")
        print(f"Average Loss: ₹{risk_metrics['avg_loss']:.2f}")
        print(f"Profit Factor: {risk_metrics['profit_factor']:.2f}")

def demo_api_integration():
    """Demonstrate API integration capabilities (without actual API calls)"""
    
    print("\n" + "=" * 70)
    print("API INTEGRATION DEMO")
    print("=" * 70)
    
    print("This demo shows how the robot would integrate with Fyers API:")
    print("\n1. AUTHENTICATION:")
    print("   - Connect using App ID, Secret, and Access Token")
    print("   - Validate credentials and get user profile")
    print("   - Initialize WebSocket for real-time data")
    
    print("\n2. MARKET DATA:")
    print("   - Fetch historical OHLCV data for technical analysis")
    print("   - Get real-time quotes for current prices")
    print("   - Monitor market depth for liquidity analysis")
    
    print("\n3. ORDER MANAGEMENT:")
    print("   - Place buy/sell orders for options")
    print("   - Set stop loss and target orders")
    print("   - Monitor order status and fills")
    
    print("\n4. POSITION TRACKING:")
    print("   - Get current positions and P&L")
    print("   - Monitor margin requirements")
    print("   - Track daily trading limits")
    
    print("\n5. RISK MONITORING:")
    print("   - Real-time position monitoring")
    print("   - Automatic stop loss execution")
    print("   - Daily loss limit enforcement")
    
    print("\nTo enable live trading:")
    print("1. Set up Fyers API credentials in .env file")
    print("2. Run: python main.py --demo (for paper trading)")
    print("3. Run: python main.py (for live trading)")

def main():
    """Run enhanced demo"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("ENHANCED TRADING ROBOT DEMO")
    print("This demo shows realistic signal generation and comprehensive testing")
    print("=" * 70)
    
    try:
        demo_signal_generation()
        demo_comprehensive_risk_management()
        demo_api_integration()
        
        print("\n" + "=" * 70)
        print("ENHANCED DEMO COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nThe trading robot is ready for deployment!")
        print("\nNext steps:")
        print("1. Configure your Fyers API credentials")
        print("2. Test with paper trading mode")
        print("3. Deploy for live trading (with caution)")
        print("\n⚠️  IMPORTANT: Always test thoroughly before live trading!")
        
    except Exception as e:
        print(f"Enhanced demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
