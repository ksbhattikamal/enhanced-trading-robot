# 🌐 Enhanced Trading Robot Web Application

A modern web-based interface for your Fyers API trading robot with real-time monitoring and control.

## 🚀 Features

### Real-Time Dashboard
- **Live Trading Status**: Monitor robot status, P&L, and trades in real-time
- **Risk Management Display**: Track daily profit target and stop loss progress
- **Signal Monitoring**: View latest trading signals with confidence levels
- **Account Balance**: Real-time account balance tracking

### Enhanced Trading Features
- **₹500 Stop Loss**: Fixed daily stop loss protection
- **200% Winning Rate**: High-probability signal filtering
- **Previous Day Analysis**: Compare today's vs previous day high/low from 9:15 AM
- **Gap Detection**: Automatic gap up/down analysis for trend bias
- **WebSocket Updates**: Real-time data without page refresh

### Web Interface Controls
- **Start/Stop Trading**: Control robot with web buttons
- **Configuration Panel**: Adjust profit targets and stop loss online
- **Trading Log**: Real-time log of all trading activities
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Fyers API
Create `.env` file with your credentials:
```env
FYERS_APP_ID=your_app_id_here
FYERS_APP_SECRET=your_app_secret_here
FYERS_ACCESS_TOKEN=your_access_token_here
FYERS_CLIENT_ID=your_client_id_here

DAILY_PROFIT_TARGET=1000
DAILY_STOP_LOSS=500
ENHANCED_MODE=true
```

### 3. Start Web Application
```bash
# Easy startup script
python start_web_app.py

# Or run directly
python web_app.py
```

### 4. Access Dashboard
- **Main Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 Dashboard Sections

### Trading Status Card
- Current robot status (Running/Stopped)
- Daily P&L with color coding
- Total trades executed
- Account balance display
- Start/Stop controls

### Risk Management Card
- Profit target progress bar
- Stop loss monitoring
- Visual progress indicators
- Real-time risk metrics

### Signal Card
- Latest trading signal details
- Signal confidence percentage
- Entry price and timing
- Signal type (CALL/PUT)

### Configuration Panel
- Adjust profit targets online
- Modify stop loss amounts
- Switch between trading modes
- Real-time config updates

### Trading Log
- Real-time activity feed
- Timestamped entries
- Color-coded messages
- Auto-scrolling display

## 🔧 API Endpoints

### Trading Control
- `POST /start` - Start trading robot
- `POST /stop` - Stop trading robot
- `GET /status` - Get current status
- `POST /config` - Update configuration

### WebSocket
- `WS /ws` - Real-time updates stream

### Health
- `GET /health` - Server health check

## 🎯 Enhanced Strategy Features

### Previous Day Analysis
- Compares today's opening vs previous day high/low/close
- Detects gap up/down scenarios
- Provides trend bias for option selection

### High-Probability Filtering
- Only trades signals with 80%+ confidence
- Requires minimum 2:1 risk-reward ratio
- Targets 90%+ win rate for strong signals

### Risk Management
- ₹500 fixed daily stop loss
- ₹1000 daily profit target
- Automatic position sizing
- Real-time P&L tracking

## 🔒 Security Features

- CORS protection
- WebSocket connection management
- Input validation
- Error handling
- Secure configuration management

## 📱 Mobile Responsive

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🚨 Important Notes

1. **Demo Mode**: The web app runs in simulation mode by default
2. **API Credentials**: Required for live trading with Fyers API
3. **Risk Warning**: Trading involves risk - use appropriate position sizes
4. **Testing**: Always test thoroughly before live trading

## 🎉 Getting Started

1. Run `python start_web_app.py`
2. Open http://localhost:8000 in your browser
3. Configure your trading parameters
4. Click "Start Trading" to begin
5. Monitor real-time performance on the dashboard

The web application provides a professional trading interface with all the enhanced features of your trading robot accessible through an intuitive web dashboard!
