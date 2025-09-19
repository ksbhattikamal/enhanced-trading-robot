# Trading Robot for Fyers API

A Python-based algorithmic trading robot that integrates with the Fyers trading platform to analyze market data and generate automated trading signals for Nifty, Bank Nifty, and Finnifty indices.

## Features

- **Real-time Market Analysis**: Analyzes current and previous day high/low data
- **Technical Indicators**: Uses EMA (Exponential Moving Average), RSI, MACD, Bollinger Bands, and other technical indicators
- **Strategy Generation**: Generates call and put option signals based on technical analysis
- **Risk Management**: Automatic stop loss and target setting with comprehensive risk management
- **Multi-Index Support**: Supports Nifty, Bank Nifty, and Finnifty trading
- **Position Monitoring**: Real-time position monitoring and exit condition checking
- **Comprehensive Logging**: Detailed logging of all trading activities

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment template and configure your settings:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your Fyers API credentials and trading preferences

## Configuration

### Fyers API Setup

1. Create an account on [Fyers](https://fyers.in/)
2. Create an API app in the [Fyers API Dashboard](https://myapi.fyers.in/dashboard)
3. Get your App ID, App Secret, and generate access token
4. Update the `.env` file with your credentials:

```env
FYERS_APP_ID=your_app_id_here
FYERS_APP_SECRET=your_app_secret_here
FYERS_ACCESS_TOKEN=your_access_token_here
FYERS_CLIENT_ID=your_client_id_here
```

### Risk Management Settings

Configure risk parameters in the `.env` file:

```env
MAX_RISK_PER_TRADE=0.02          # 2% risk per trade
MAX_DAILY_LOSS=0.05              # 5% maximum daily loss
POSITION_SIZE_PERCENT=0.1        # 10% of capital per position
STOP_LOSS_PERCENT=0.015          # 1.5% stop loss
TARGET_PROFIT_PERCENT=0.03       # 3% target profit
```

### Technical Analysis Settings

```env
EMA_PERIOD_SHORT=9               # Short EMA period
EMA_PERIOD_LONG=21               # Long EMA period
```

## Usage

### Running the Trading Robot

```bash
# Run in demo mode (recommended for testing)
python main.py --demo

# Run in live mode (actual trading)
python main.py
```

### Key Components

1. **FyersClient**: Handles all API interactions with Fyers
2. **TechnicalAnalysis**: Calculates technical indicators and market analysis
3. **TradingStrategy**: Generates trading signals based on technical analysis
4. **RiskManager**: Manages risk, position sizing, and exit conditions
5. **Main**: Orchestrates the entire trading process

## Strategy Logic

The trading robot uses a combination of technical indicators to generate signals:

### Signal Generation
- **EMA Crossover**: Short EMA vs Long EMA for trend direction
- **RSI**: Relative Strength Index for overbought/oversold conditions
- **MACD**: Moving Average Convergence Divergence for momentum
- **Bollinger Bands**: For volatility-based signals
- **Support/Resistance**: Previous day high/low analysis

### Entry Conditions

**Call Signals (Bullish)**:
- Short EMA > Long EMA
- Price > Short EMA
- RSI < 70 (not overbought)
- MACD > Signal line
- High breakout from previous day

**Put Signals (Bearish)**:
- Short EMA < Long EMA
- Price < Short EMA
- RSI > 30 (not oversold)
- MACD < Signal line
- Low breakdown from previous day

### Risk Management

- **Position Sizing**: Based on account balance and risk per trade
- **Stop Loss**: Automatic stop loss based on technical levels or percentage
- **Target Setting**: Profit targets based on risk-reward ratios
- **Daily Limits**: Maximum daily loss and trade count limits
- **Correlation Limits**: Prevents over-exposure to correlated positions

## File Structure

```
trading_robot/
├── main.py                 # Main trading robot orchestrator
├── config.py              # Configuration management
├── fyers_client.py        # Fyers API client wrapper
├── technical_analysis.py  # Technical indicator calculations
├── strategy.py            # Trading strategy and signal generation
├── risk_manager.py        # Risk management and position tracking
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Logging

The robot generates comprehensive logs in `trading_robot.log` including:
- Market analysis results
- Signal generation details
- Trade recommendations
- Risk management decisions
- Position monitoring updates
- Daily trading summaries

## Important Notes

### Demo Mode
- Always test in demo mode first
- Demo mode logs all trading decisions without placing actual orders
- Use `--demo` flag to run in demo mode

### Risk Warnings
- **This is for educational purposes only**
- **Always test thoroughly before live trading**
- **Never risk more than you can afford to lose**
- **Past performance does not guarantee future results**
- **Markets can be unpredictable and losses can occur**

### Market Hours
- The robot automatically detects market hours (9:15 AM - 3:30 PM IST)
- Positions are automatically closed at end of day
- Weekend trading is disabled

## Customization

### Adding New Indicators
Add new technical indicators in `technical_analysis.py`:

```python
def calculate_custom_indicator(self, data: pd.Series) -> pd.Series:
    # Your custom indicator logic
    return result
```

### Modifying Strategy
Update signal generation logic in `strategy.py`:

```python
def _evaluate_signal(self, trend_analysis: Dict, high_low_analysis: Dict, symbol: str):
    # Your custom strategy logic
    return signal_data
```

### Adjusting Risk Parameters
Modify risk management rules in `risk_manager.py`:

```python
def check_risk_limits(self, signal: Dict, account_balance: float):
    # Your custom risk management logic
    return risk_check
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check your Fyers credentials in `.env`
   - Ensure your access token is valid
   - Verify internet connection

2. **Insufficient Data**
   - Check if market is open
   - Verify symbol names are correct
   - Ensure sufficient historical data is available

3. **No Signals Generated**
   - Market conditions may not meet strategy criteria
   - Check confidence thresholds in strategy
   - Review technical indicator calculations

### Debug Mode
Enable debug logging by modifying the log level in the code:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Support

For issues related to:
- **Fyers API**: Contact [Fyers Support](https://support.fyers.in)
- **Trading Robot**: Check logs and review configuration
- **Technical Issues**: Review the code and documentation

## Disclaimer

This trading robot is provided for educational and research purposes only. The authors are not responsible for any financial losses incurred through the use of this software. Always conduct thorough testing and consider consulting with financial advisors before engaging in algorithmic trading.

**Trading involves substantial risk and is not suitable for all investors. Past performance is not indicative of future results.**
