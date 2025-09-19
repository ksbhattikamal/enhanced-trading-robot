#!/usr/bin/env python3

"""
Test script for enhanced strategy functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_strategy import EnhancedTradingStrategy
from config import Config
import pandas as pd
import numpy as np

def test_enhanced_strategy():
    """Test the enhanced strategy functionality"""
    
    print("=" * 70)
    print("TESTING ENHANCED STRATEGY")
    print("=" * 70)
    
    try:
        config = Config()
        strategy = EnhancedTradingStrategy()
        
        data = pd.DataFrame({
            'open': np.random.uniform(19500, 19700, 50),
            'high': np.random.uniform(19600, 19800, 50),
            'low': np.random.uniform(19400, 19600, 50),
            'close': np.random.uniform(19500, 19700, 50),
            'volume': np.random.randint(1000, 10000, 50)
        })
        
        strategy.set_previous_day_data(19650, 19450, 19600)
        
        signal = strategy.generate_high_probability_signals('NIFTY', data)
        
        print(f"Signal: {signal.get('signal', 'NO_SIGNAL')}")
        print(f"Confidence: {signal.get('confidence', 0)}%")
        print("✅ Enhanced strategy test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced strategy test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_strategy()
    sys.exit(0 if success else 1)
