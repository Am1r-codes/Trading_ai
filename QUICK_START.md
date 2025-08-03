# 🚀 Quick Start Guide

## Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Keys

1. Copy the environment template:
```bash
copy env.example .env
```

2. Edit `.env` file and add your API keys:
```env
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
SECRET_KEY=your-secret-key-for-sessions
```

## Step 3: Start the Application

### Option A: Using the batch file (Windows)
```bash
start.bat
```

### Option B: Manual start
```bash
python run.py
```

## Step 4: Open the Frontend

1. Open `frontend/index.html` in your browser
2. Or serve with a local server:
```bash
cd frontend
python -m http.server 8000
# Navigate to http://localhost:8000
```

## Step 5: Test the Installation

```bash
python test_installation.py
```

## 📊 Usage Examples

### Chat Interface
```
You: Analyze GOLD
AI: ✅ GOLD selected. What's the current price?

You: 3368
AI: Price recorded. What timeframe?

You: 15M
AI: ✅ Timeframe selected. Account details?

You: Personal 2500
AI: Ready to analyze! [Full analysis provided]
```

### Supported Assets
- **Forex**: EURUSD, GBPUSD, USDJPY
- **Commodities**: GOLD, SILVER, OIL  
- **Crypto**: BITCOIN, ETHEREUM
- **Stocks**: SPY, QQQ, AAPL

## 🔧 Troubleshooting

### Common Issues:

1. **"No module named 'flask'"**
   - Run: `pip install -r requirements.txt`

2. **API Key Errors**
   - Check your `.env` file
   - Verify API keys are correct

3. **Connection Issues**
   - Ensure backend is running on port 5000
   - Check if frontend can connect to backend

### Get API Keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/account/keys

## 📁 Project Structure

```
trading_ai/
├── backend/
│   └── trading_assistant_backend.py
├── frontend/
│   ├── index.html
│   └── connector.js
├── data/
├── logs/
├── run.py
├── requirements.txt
├── env.example
├── README.md
└── start.bat
```

## 🎯 Next Steps

1. **Test with Paper Trading**: Start with small amounts
2. **Review AI Signals**: Don't follow blindly
3. **Monitor Performance**: Track your results
4. **Learn Smart Money Concepts**: Study order blocks, liquidity zones
5. **Practice Risk Management**: Never risk more than 2-3% per trade

---

**⚠️ Important**: This is for educational purposes only. Trading carries risk. Never invest more than you can afford to lose.

Good luck and trade safely! 🚀 