# Trading Assistant Setup & Deployment Guide

## 📋 Requirements

### Python Dependencies (requirements.txt)
```txt
flask==2.3.3
flask-cors==4.0.0
flask-socketio==5.3.4
python-socketio==5.9.0
openai==0.28.0
anthropic==0.7.0
yfinance==0.2.28
pandas==2.0.3
numpy==1.24.3
ta==0.10.2
requests==2.31.0
python-dotenv==1.0.0
```

### Environment Variables (.env)
```env
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ALPHA_VANTAGE_KEY=your-alpha-vantage-key-here
SECRET_KEY=your-secret-key-for-sessions
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Create project directory
mkdir trading-assistant
cd trading-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

#### Get API Keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/account/keys
- **Alpha Vantage** (free): https://www.alphavantage.co/support/#api-key

Create `.env` file with your keys.

### 3. Run the Application

```bash
# Start the backend
python trading_assistant_backend.py

# The backend will run on http://localhost:5000
```

### 4. Open the Frontend
- Save the HTML file as `index.html`
- Open it in your browser
- Or serve it with a simple HTTP server:
```bash
python -m http.server 8000
# Navigate to http://localhost:8000
```

## 🔧 Configuration

### Frontend Configuration
Update the API endpoint in the HTML file:
```javascript
// Line to modify in the HTML
const API_URL = 'http://localhost:5000';  // Change this to your backend URL
```

### Backend Configuration
Modify these settings in `trading_assistant_backend.py`:

```python
# Risk management defaults
DEFAULT_RISK_PERCENT = 2.5  # Maximum risk per trade
MAX_POSITION_SIZE = 5.0     # Maximum lots

# Analysis settings
CONFIDENCE_THRESHOLD = 70   # Minimum confidence for trade signals
MAX_TRADES_PER_DAY = 3     # Daily trade limit
```

## 🌐 Deployment Options

### Option 1: Local Deployment (Personal Use)
Perfect for personal use on your computer.

### Option 2: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "trading_assistant_backend.py"]
```

Build and run:
```bash
docker build -t trading-assistant .
docker run -p 5000:5000 --env-file .env trading-assistant
```

### Option 3: Cloud Deployment (Heroku)

Create `Procfile`:
```
web: gunicorn --worker-class eventlet -w 1 trading_assistant_backend:app
```

Add to requirements.txt:
```
gunicorn==21.2.0
eventlet==0.33.3
```

Deploy:
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key
heroku config:set ANTHROPIC_API_KEY=your-key
git push heroku main
```

### Option 4: VPS Deployment

1. Get a VPS (DigitalOcean, Linode, etc.)
2. Install Python and nginx
3. Use systemd for process management
4. Set up SSL with Let's Encrypt

## 📊 Data Sources Configuration

### Free Market Data APIs

1. **Yahoo Finance** (already integrated via yfinance)
   - No API key needed
   - Real-time for most assets

2. **Alpha Vantage** (free tier)
   - 5 API calls per minute
   - 500 calls per day
   - Good for forex and crypto

3. **Twelve Data** (free tier)
   - Sign up at: https://twelvedata.com
   - 800 API calls/day
   - WebSocket for real-time

### Premium Options (Better for Production)

1. **Polygon.io**
   - $29/month starter
   - Real-time data
   - Historical data

2. **IEX Cloud**
   - Pay as you go
   - Reliable and fast

## 🔒 Security Best Practices

### 1. API Key Security
```python
# Never hardcode API keys
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

### 2. Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/analyze')
@limiter.limit("10 per minute")
def analyze():
    # Your code
```

### 3. Input Validation
```python
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField
from wtforms.validators import DataRequired, NumberRange

class TradingForm(FlaskForm):
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    asset = StringField('Asset', validators=[DataRequired()])
```

## 🎨 Customization

### Adding New Assets
```python
SUPPORTED_ASSETS = {
    'GOLD': 'GC=F',
    'SILVER': 'SI=F',
    'OIL': 'CL=F',
    'EURUSD': 'EURUSD=X',
    'GBPUSD': 'GBPUSD=X',
    'BITCOIN': 'BTC-USD',
    'ETHEREUM': 'ETH-USD',
    'SPY': 'SPY',
    'QQQ': 'QQQ'
}
```

### Custom Indicators
```python
def calculate_custom_indicator(df):
    # Add your custom indicator logic
    df['Custom_Signal'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    return df
```

### Modify AI Behavior
```python
# In TradingAI class
self.system_prompt = """
Your custom instructions here...
Focus on: [your strategies]
Risk level: [conservative/moderate/aggressive]
"""
```

## 📈 Performance Optimization

### 1. Caching Market Data
```python
from functools import lru_cache
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=100)
def get_cached_price(symbol):
    # Cache for 60 seconds
    cached = cache.get(f"price:{symbol}")
    if cached:
        return json.loads(cached)
    
    price = fetch_price(symbol)
    cache.setex(f"price:{symbol}", 60, json.dumps(price))
    return price
```

### 2. Database for History
```python
import sqlite3

def setup_database():
    conn = sqlite3.connect('trades.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME,
            asset TEXT,
            entry REAL,
            stop_loss REAL,
            take_profit REAL,
            result TEXT
        )
    ''')
    conn.commit()
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify keys in `.env` file
   - Check API quotas/limits
   - Ensure keys have proper permissions

2. **Connection Issues**
   - Check CORS settings
   - Verify backend is running
   - Update API_URL in frontend

3. **Data Not Loading**
   - Check internet connection
   - Verify market is open
   - Try different asset symbols

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

app.config['DEBUG'] = True
```

## 📝 Testing

### Unit Tests
```python
# test_trading.py
import unittest
from trading_assistant_backend import TradingAI, MarketDataFetcher

class TestTrading(unittest.TestCase):
    def test_position_sizing(self):
        # Test position size calculation
        pass
    
    def test_market_data(self):
        # Test data fetching
        pass

if __name__ == '__main__':
    unittest.main()
```

## 🚨 Disclaimer

**IMPORTANT**: This trading assistant is for educational purposes only. 

- Always verify signals with your own analysis
- Never risk more than you can afford to lose
- Past performance doesn't guarantee future results
- The creators are not responsible for any trading losses
- Consider paper trading first

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Test with mock data first
4. Use conservative risk settings

## 🎯 Next Steps

1. **Start with Paper Trading**: Test the system without real money
2. **Backtest Strategies**: Validate signals against historical data
3. **Monitor Performance**: Track win rate and risk metrics
4. **Iterate and Improve**: Refine based on results
5. **Stay Educated**: Continue learning about markets and risk management

---

**Remember**: Successful trading requires discipline, continuous learning, and proper risk management. This tool is meant to assist, not replace, your own analysis and judgment.