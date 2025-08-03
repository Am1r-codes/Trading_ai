# NORO AI Trading Assistant

A comprehensive AI-powered trading assistant that combines advanced market analysis with smart money concepts and real-time data integration.

## 🚀 Live Demo

[Deployed on Lovable.dev](https://your-app.lovable.dev) - Coming Soon!

## ✨ Features

- **AI-Powered Analysis**: OpenAI/Claude integration for intelligent market analysis
- **Smart Money Concepts**: Order blocks, liquidity zones, fair value gaps
- **Real-Time Data**: Live market feeds and price updates
- **Risk Management**: Position sizing, Kelly criterion, drawdown protection
- **Trade Journal**: Complete history and performance tracking
- **Professional Dashboard**: TradingView charts with custom indicators
- **WebSocket Support**: Real-time updates and live data streaming

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SocketIO
- **Frontend**: HTML5, CSS3, JavaScript
- **AI**: OpenAI GPT-4, Anthropic Claude
- **Data**: Yahoo Finance, Technical Analysis
- **Deployment**: Lovable.dev

## 🚀 Quick Start

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/trading-ai.git
   cd trading-ai
   ```

2. **Install dependencies**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   copy env.example .env
   # Edit .env and add your API keys
   ```

4. **Start the application**:
   ```bash
   start.bat
   # Or manually: python run.py
   ```

5. **Open the frontend**:
   - Double-click: `frontend/index.html`
   - Or serve: `cd frontend && python -m http.server 8000`

## 🌐 Deployment

### Lovable.dev (Recommended)

1. **Fork this repository**
2. **Go to**: https://lovable.dev/
3. **Connect your GitHub account**
4. **Create new project** and select this repository
5. **Add environment variables**:
   ```
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   SECRET_KEY=your-secret-key
   PORT=5000
   ```
6. **Deploy!**

### Other Platforms

- **Railway**: Use `railway.json`
- **Render**: Use `render.yaml`
- **Heroku**: Use `Procfile`

## 📊 Usage

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

## 🔧 API Endpoints

- `GET /api/market-data/<symbol>` - Get real-time market data
- `POST /api/chat` - Chat with AI assistant
- `POST /api/analyze` - Perform trading analysis
- `POST /api/calculate-position` - Calculate position size

## 🔒 Environment Variables

```env
# AI APIs (Required)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Application Settings
SECRET_KEY=your-secret-key
PORT=5000
DEBUG=False

# Risk Management
MAX_RISK_PER_TRADE=2.5
MAX_DAILY_LOSS=500
MAX_WEEKLY_LOSS=1500
```

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
├── start.bat
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details.

## ⚠️ Disclaimer

**TRADING DISCLAIMER**: This software is for educational purposes only. Trading carries significant risk and may not be suitable for all investors. Past performance does not guarantee future results.

**NO FINANCIAL ADVICE**: This software does not constitute financial advice. Always do your own research and never invest more than you can afford to lose.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the docs folder
- **Community**: Join our discussions

---

**Remember**: Success in trading requires discipline, continuous learning, and proper risk management. This tool is meant to assist your analysis, not replace your judgment.

Good luck and trade safely! 🚀 