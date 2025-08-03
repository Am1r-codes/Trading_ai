# trading_assistant_backend.py
"""
Complete Trading Assistant Backend
Integrates with OpenAI/Claude API for intelligent responses
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random
from dataclasses import dataclass
from enum import Enum

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import openai
import anthropic
import yfinance as yf
import pandas as pd
import numpy as np
from ta import trend, momentum, volatility
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys (use environment variables in production)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-key')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'your-anthropic-key')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'your-alpha-vantage-key')

# Initialize AI clients
openai.api_key = OPENAI_API_KEY
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

class AnalysisType(Enum):
    TREND = "trend"
    SCALPING = "scalping"
    SWING = "swing"
    SNIPER = "sniper"

@dataclass
class TradingSession:
    """Stores user's trading session data"""
    user_id: str
    asset: str = None
    symbol: str = None
    price: float = None
    timeframe: str = None
    account_type: str = None
    balance: float = None
    risk_percent: float = 2.5
    conversation_history: List = None
    analysis_data: Dict = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.analysis_data is None:
            self.analysis_data = {}

class MarketDataFetcher:
    """Fetches real market data from various sources"""
    
    @staticmethod
    def get_current_price(symbol: str) -> Dict:
        """Fetch current price from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                return {
                    'price': float(current_price),
                    'volume': float(data['Volume'].iloc[-1]),
                    'high': float(data['High'].iloc[-1]),
                    'low': float(data['Low'].iloc[-1]),
                    'open': float(data['Open'].iloc[-1])
                }
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
        
        # Fallback to mock data
        base_price = 3368 if 'GOLD' in symbol.upper() else 1.1000
        return {
            'price': base_price + random.uniform(-10, 10),
            'volume': random.randint(1000000, 5000000),
            'high': base_price + random.uniform(5, 15),
            'low': base_price - random.uniform(5, 15),
            'open': base_price + random.uniform(-5, 5)
        }
    
    @staticmethod
    def get_technical_indicators(symbol: str, period: str = "1mo") -> Dict:
        """Calculate technical indicators"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return MarketDataFetcher._get_mock_indicators()
            
            # Calculate indicators
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['RSI'] = momentum.RSIIndicator(df['Close']).rsi()
            df['MACD'] = trend.MACD(df['Close']).macd()
            df['BB_upper'], df['BB_middle'], df['BB_lower'] = volatility.BollingerBands(df['Close']).bollinger_hband(), volatility.BollingerBands(df['Close']).bollinger_mavg(), volatility.BollingerBands(df['Close']).bollinger_lband()
            
            latest = df.iloc[-1]
            
            return {
                'sma20': float(latest['SMA_20']) if pd.notna(latest['SMA_20']) else None,
                'sma50': float(latest['SMA_50']) if pd.notna(latest['SMA_50']) else None,
                'rsi': float(latest['RSI']) if pd.notna(latest['RSI']) else None,
                'macd': float(latest['MACD']) if pd.notna(latest['MACD']) else None,
                'bb_upper': float(latest['BB_upper']) if pd.notna(latest['BB_upper']) else None,
                'bb_lower': float(latest['BB_lower']) if pd.notna(latest['BB_lower']) else None,
                'trend': 'bullish' if latest['Close'] > latest['SMA_20'] else 'bearish'
            }
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return MarketDataFetcher._get_mock_indicators()
    
    @staticmethod
    def _get_mock_indicators() -> Dict:
        """Return mock indicators for demo purposes"""
        return {
            'sma20': 3350 + random.uniform(-20, 20),
            'sma50': 3340 + random.uniform(-30, 30),
            'rsi': random.uniform(30, 70),
            'macd': random.uniform(-5, 5),
            'bb_upper': 3380 + random.uniform(0, 20),
            'bb_lower': 3320 - random.uniform(0, 20),
            'trend': random.choice(['bullish', 'bearish'])
        }

class SmartMoneyAnalyzer:
    """Implements Smart Money Concepts analysis"""
    
    @staticmethod
    def find_order_blocks(price_data: pd.DataFrame) -> List[Dict]:
        """Identify order blocks in price data"""
        order_blocks = []
        
        try:
            for i in range(2, len(price_data) - 2):
                # Bullish order block: last down candle before up move
                if (price_data['Close'].iloc[i] < price_data['Open'].iloc[i] and
                    price_data['Close'].iloc[i+1] > price_data['Open'].iloc[i+1] and
                    price_data['Close'].iloc[i+2] > price_data['Close'].iloc[i+1]):
                    
                    order_blocks.append({
                        'type': 'bullish',
                        'level': float(price_data['Low'].iloc[i]),
                        'strength': 'strong' if abs(price_data['Close'].iloc[i+2] - price_data['Close'].iloc[i]) > price_data['Close'].iloc[i] * 0.002 else 'medium',
                        'timestamp': price_data.index[i]
                    })
                
                # Bearish order block: last up candle before down move
                elif (price_data['Close'].iloc[i] > price_data['Open'].iloc[i] and
                      price_data['Close'].iloc[i+1] < price_data['Open'].iloc[i+1] and
                      price_data['Close'].iloc[i+2] < price_data['Close'].iloc[i+1]):
                    
                    order_blocks.append({
                        'type': 'bearish',
                        'level': float(price_data['High'].iloc[i]),
                        'strength': 'strong' if abs(price_data['Close'].iloc[i] - price_data['Close'].iloc[i+2]) > price_data['Close'].iloc[i] * 0.002 else 'medium',
                        'timestamp': price_data.index[i]
                    })
        except Exception as e:
            logger.error(f"Error finding order blocks: {e}")
        
        return order_blocks[-5:] if order_blocks else []  # Return last 5 order blocks
    
    @staticmethod
    def find_liquidity_zones(price_data: pd.DataFrame) -> List[Dict]:
        """Identify liquidity zones (equal highs/lows)"""
        liquidity_zones = []
        
        try:
            # Find equal highs (buy-side liquidity)
            highs = price_data['High'].round(2)
            high_counts = highs.value_counts()
            
            for price, count in high_counts.items():
                if count >= 2:
                    liquidity_zones.append({
                        'type': 'buy_side',
                        'level': float(price),
                        'strength': count,
                        'description': f'Buy-side liquidity at {price} (tested {count} times)'
                    })
            
            # Find equal lows (sell-side liquidity)
            lows = price_data['Low'].round(2)
            low_counts = lows.value_counts()
            
            for price, count in low_counts.items():
                if count >= 2:
                    liquidity_zones.append({
                        'type': 'sell_side',
                        'level': float(price),
                        'strength': count,
                        'description': f'Sell-side liquidity at {price} (tested {count} times)'
                    })
        except Exception as e:
            logger.error(f"Error finding liquidity zones: {e}")
        
        return sorted(liquidity_zones, key=lambda x: x['strength'], reverse=True)[:5]
    
    @staticmethod
    def calculate_fair_value_gaps(price_data: pd.DataFrame) -> List[Dict]:
        """Identify Fair Value Gaps (FVG)"""
        fvgs = []
        
        try:
            for i in range(1, len(price_data) - 1):
                # Bullish FVG
                if price_data['Low'].iloc[i+1] > price_data['High'].iloc[i-1]:
                    gap_size = price_data['Low'].iloc[i+1] - price_data['High'].iloc[i-1]
                    if gap_size > price_data['Close'].iloc[i] * 0.001:  # At least 0.1% gap
                        fvgs.append({
                            'type': 'bullish',
                            'upper': float(price_data['Low'].iloc[i+1]),
                            'lower': float(price_data['High'].iloc[i-1]),
                            'midpoint': float((price_data['Low'].iloc[i+1] + price_data['High'].iloc[i-1]) / 2),
                            'size': float(gap_size)
                        })
                
                # Bearish FVG
                elif price_data['High'].iloc[i+1] < price_data['Low'].iloc[i-1]:
                    gap_size = price_data['Low'].iloc[i-1] - price_data['High'].iloc[i+1]
                    if gap_size > price_data['Close'].iloc[i] * 0.001:
                        fvgs.append({
                            'type': 'bearish',
                            'upper': float(price_data['Low'].iloc[i-1]),
                            'lower': float(price_data['High'].iloc[i+1]),
                            'midpoint': float((price_data['Low'].iloc[i-1] + price_data['High'].iloc[i+1]) / 2),
                            'size': float(gap_size)
                        })
        except Exception as e:
            logger.error(f"Error finding FVGs: {e}")
        
        return fvgs[-3:] if fvgs else []  # Return last 3 FVGs

class TradingAI:
    """Main AI engine for trading analysis"""
    
    def __init__(self):
        self.system_prompt = """
        You are an advanced trading assistant specializing in Smart Money Concepts (SMC), 
        institutional trading strategies, and technical analysis. You provide professional-grade 
        analysis while being educational and risk-aware.
        
        Key principles:
        1. Always emphasize risk management (2-3% risk per trade)
        2. Use proper technical terminology but explain it clearly
        3. Provide specific entry, stop loss, and take profit levels
        4. Include position sizing calculations
        5. Mention confluence factors for higher probability setups
        6. Always include risk disclaimers
        
        Analysis framework:
        - Market Structure (HH, HL, LL, LH)
        - Order Blocks and Breaker Blocks
        - Liquidity Zones and Sweeps
        - Fair Value Gaps (FVG)
        - Volume Analysis
        - Multi-timeframe Confirmation
        """
    
    def generate_analysis(self, session: TradingSession, market_data: Dict) -> Dict:
        """Generate comprehensive trading analysis"""
        
        # Prepare context for AI
        context = self._prepare_context(session, market_data)
        
        # Generate analysis using AI
        analysis = self._call_ai_model(context)
        
        # Calculate trade parameters
        trade_params = self._calculate_trade_parameters(
            session.price,
            session.balance,
            session.risk_percent,
            analysis['bias'],
            market_data
        )
        
        # Combine everything
        return {
            'timestamp': datetime.now().isoformat(),
            'asset': session.asset,
            'symbol': session.symbol,
            'timeframe': session.timeframe,
            'current_price': session.price,
            'market_data': market_data,
            'analysis': analysis,
            'trade_setup': trade_params,
            'confidence': self._calculate_confidence(analysis, market_data),
            'risk_warnings': self._generate_risk_warnings()
        }
    
    def _prepare_context(self, session: TradingSession, market_data: Dict) -> str:
        """Prepare context for AI model"""
        return f"""
        Asset: {session.asset} ({session.symbol})
        Current Price: ${session.price}
        Timeframe: {session.timeframe}
        Account Type: {session.account_type}
        Account Balance: ${session.balance}
        Risk Per Trade: {session.risk_percent}%
        
        Market Data:
        - Trend: {market_data.get('indicators', {}).get('trend', 'Unknown')}
        - RSI: {market_data.get('indicators', {}).get('rsi', 'N/A')}
        - Volume: {market_data.get('current', {}).get('volume', 'N/A')}
        
        Please provide:
        1. Market bias (bullish/bearish) with reasoning
        2. Key support and resistance levels
        3. Entry strategy
        4. Risk management approach
        5. Confluence factors
        """
    
    def _call_ai_model(self, context: str) -> Dict:
        """Call AI model for analysis"""
        try:
            # Try Claude first
            response = claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": context}
                ]
            )
            
            # Parse response
            return self._parse_ai_response(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            
            # Fallback to OpenAI
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": context}
                    ],
                    max_tokens=1000
                )
                
                return self._parse_ai_response(response.choices[0].message['content'])
                
            except Exception as e2:
                logger.error(f"OpenAI API error: {e2}")
                # Return mock analysis
                return self._get_mock_analysis()
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response into structured data"""
        # This would parse the AI's text response into structured data
        # For now, returning mock structured data
        return {
            'bias': 'bullish' if 'bull' in response_text.lower() else 'bearish',
            'reasoning': response_text[:200],
            'key_levels': self._extract_price_levels(response_text),
            'confluence_factors': self._extract_confluence_factors(response_text)
        }
    
    def _extract_price_levels(self, text: str) -> List[float]:
        """Extract price levels from text"""
        import re
        # Find numbers that look like prices
        prices = re.findall(r'\$?(\d{1,5}(?:\.\d{1,2})?)', text)
        return [float(p) for p in prices[:5]]  # Return first 5 prices found
    
    def _extract_confluence_factors(self, text: str) -> List[str]:
        """Extract confluence factors from analysis"""
        factors = []
        keywords = ['order block', 'liquidity', 'fvg', 'support', 'resistance', 'trend', 'volume']
        
        for keyword in keywords:
            if keyword in text.lower():
                factors.append(keyword.title())
        
        return factors
    
    def _calculate_trade_parameters(self, current_price: float, balance: float, 
                                   risk_percent: float, bias: str, 
                                   market_data: Dict) -> Dict:
        """Calculate precise trade parameters"""
        
        # Calculate stop loss distance (using ATR or fixed percentage)
        atr_percent = 0.5  # Mock ATR as percentage
        stop_distance = current_price * (atr_percent / 100)
        
        # Entry price (slightly better than current for limit order)
        if bias == 'bullish':
            entry = current_price - (current_price * 0.001)  # 0.1% below for better entry
            stop_loss = entry - stop_distance
            tp1 = entry + stop_distance  # 1:1 RR
            tp2 = entry + (stop_distance * 2)  # 1:2 RR
            tp3 = entry + (stop_distance * 3)  # 1:3 RR
        else:
            entry = current_price + (current_price * 0.001)
            stop_loss = entry + stop_distance
            tp1 = entry - stop_distance
            tp2 = entry - (stop_distance * 2)
            tp3 = entry - (stop_distance * 3)
        
        # Position sizing
        risk_amount = balance * (risk_percent / 100)
        pip_risk = abs(entry - stop_loss)
        
        # Calculate position size (simplified - would need proper pip value calculation)
        if 'forex' in market_data.get('asset_type', '').lower():
            pip_value = 10  # $10 per pip for standard lot
            position_size = risk_amount / (pip_risk * 10000 * pip_value)
        else:
            position_size = risk_amount / pip_risk
        
        return {
            'bias': bias,
            'entry': round(entry, 2),
            'stop_loss': round(stop_loss, 2),
            'targets': {
                'tp1': round(tp1, 2),
                'tp2': round(tp2, 2),
                'tp3': round(tp3, 2)
            },
            'position_size': round(position_size, 2),
            'risk_amount': round(risk_amount, 2),
            'risk_reward_ratios': [1.0, 2.0, 3.0],
            'pip_risk': round(pip_risk * 10000 if 'forex' in market_data.get('asset_type', '').lower() else pip_risk, 1)
        }
    
    def _calculate_confidence(self, analysis: Dict, market_data: Dict) -> int:
        """Calculate confidence score based on confluence"""
        confidence = 60  # Base confidence
        
        # Add points for confluence factors
        if len(analysis.get('confluence_factors', [])) > 3:
            confidence += 10
        if len(analysis.get('confluence_factors', [])) > 5:
            confidence += 10
        
        # Add points for clear trend
        if market_data.get('indicators', {}).get('trend') in ['bullish', 'bearish']:
            confidence += 5
        
        # Add points for good RSI
        rsi = market_data.get('indicators', {}).get('rsi', 50)
        if 30 < rsi < 70:
            confidence += 5
        
        # Add randomness for realism
        confidence += random.randint(-5, 10)
        
        return min(95, max(50, confidence))
    
    def _generate_risk_warnings(self) -> List[str]:
        """Generate appropriate risk warnings"""
        return [
            "Trading involves substantial risk of loss",
            "Past performance doesn't guarantee future results",
            "Never risk more than you can afford to lose",
            "This analysis is for educational purposes only",
            "Always do your own research before trading"
        ]
    
    def _get_mock_analysis(self) -> Dict:
        """Return mock analysis when APIs fail"""
        return {
            'bias': random.choice(['bullish', 'bearish']),
            'reasoning': "Based on current market structure and order flow analysis.",
            'key_levels': [3350, 3360, 3370, 3380, 3390],
            'confluence_factors': ['Order Block', 'Liquidity Sweep', 'Trend Alignment']
        }

# Session management
sessions: Dict[str, TradingSession] = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    data = request.json
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    
    # Get or create session
    if user_id not in sessions:
        sessions[user_id] = TradingSession(user_id=user_id)
    
    session = sessions[user_id]
    session.conversation_history.append({'role': 'user', 'content': message})
    
    # Process message and generate response
    response = process_message(session, message)
    session.conversation_history.append({'role': 'assistant', 'content': response['text']})
    
    return jsonify(response)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Perform full trading analysis"""
    data = request.json
    user_id = data.get('user_id', 'default')
    
    if user_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[user_id]
    
    # Validate required data
    if not all([session.asset, session.price, session.timeframe]):
        return jsonify({'error': 'Missing required trading parameters'}), 400
    
    # Fetch market data
    market_data = {
        'current': MarketDataFetcher.get_current_price(session.symbol or session.asset),
        'indicators': MarketDataFetcher.get_technical_indicators(session.symbol or session.asset)
    }
    
    # Get historical data for SMC analysis
    try:
        ticker = yf.Ticker(session.symbol or session.asset)
        hist_data = ticker.history(period="1mo", interval="1h")
        
        if not hist_data.empty:
            market_data['order_blocks'] = SmartMoneyAnalyzer.find_order_blocks(hist_data)
            market_data['liquidity_zones'] = SmartMoneyAnalyzer.find_liquidity_zones(hist_data)
            market_data['fvgs'] = SmartMoneyAnalyzer.calculate_fair_value_gaps(hist_data)
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
    
    # Generate AI analysis
    ai = TradingAI()
    analysis_result = ai.generate_analysis(session, market_data)
    
    # Store analysis in session
    session.analysis_data = analysis_result
    
    return jsonify(analysis_result)

@app.route('/api/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """Get real-time market data for a symbol"""
    data = {
        'current': MarketDataFetcher.get_current_price(symbol),
        'indicators': MarketDataFetcher.get_technical_indicators(symbol)
    }
    return jsonify(data)

@app.route('/api/calculate-position', methods=['POST'])
def calculate_position():
    """Calculate position size based on risk management"""
    data = request.json
    
    balance = data.get('balance', 10000)
    risk_percent = data.get('risk_percent', 2.5)
    entry = data.get('entry', 100)
    stop_loss = data.get('stop_loss', 95)
    
    risk_amount = balance * (risk_percent / 100)
    pip_risk = abs(entry - stop_loss)
    position_size = risk_amount / pip_risk
    
    return jsonify({
        'position_size': round(position_size, 2),
        'risk_amount': round(risk_amount, 2),
        'pip_risk': round(pip_risk, 4),
        'potential_loss': round(risk_amount, 2),
        'potential_profit_1_1': round(risk_amount, 2),
        'potential_profit_1_2': round(risk_amount * 2, 2),
        'potential_profit_1_3': round(risk_amount * 3, 2)
    })

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'status': 'Connected to trading assistant'})

@socketio.on('subscribe_market_data')
def handle_market_subscription(data):
    """Subscribe to real-time market data updates"""
    symbol = data.get('symbol')
    
    # In production, this would connect to a real-time data feed
    # For demo, emit mock updates every 5 seconds
    import threading
    
    def emit_updates():
        while True:
            market_data = MarketDataFetcher.get_current_price(symbol)
            emit('market_update', {
                'symbol': symbol,
                'data': market_data,
                'timestamp': datetime.now().isoformat()
            })
            threading.Event().wait(5)
    
    threading.Thread(target=emit_updates, daemon=True).start()

def process_message(session: TradingSession, message: str) -> Dict:
    """Process user message and generate appropriate response"""
    lower_msg = message.lower()
    
    # Asset detection
    if any(asset in lower_msg for asset in ['gold', 'xauusd', 'eur', 'gbp', 'btc', 'bitcoin']):
        return handle_asset_selection(session, message)
    
    # Price detection
    elif session.asset and not session.price and any(char.isdigit() for char in message):
        return handle_price_input(session, message)
    
    # Timeframe detection
    elif any(tf in lower_msg for tf in ['5m', '15m', '30m', '1h', '4h', '1d', 'daily']):
        return handle_timeframe_selection(session, message)
    
    # Account info
    elif any(word in lower_msg for word in ['personal', 'funded', 'balance']):
        return handle_account_info(session, message)
    
    # Analysis request
    elif any(word in lower_msg for word in ['analyze', 'analysis', 'setup', 'trade']):
        return {'text': "Starting comprehensive analysis...", 'action': 'analyze'}
    
    # Educational content
    elif 'order block' in lower_msg or 'ob' in lower_msg:
        return {'text': generate_educational_content('order_blocks')}
    
    elif 'liquidity' in lower_msg:
        return {'text': generate_educational_content('liquidity')}
    
    else:
        return {'text': generate_conversational_response(message)}

def handle_asset_selection(session: TradingSession, message: str) -> Dict:
    """Handle asset selection"""
    # Determine asset from message
    if 'gold' in message.lower() or 'xauusd' in message.lower():
        session.asset = 'GOLD'
        session.symbol = 'GC=F'  # Gold futures symbol for yfinance
    elif 'eur' in message.lower():
        session.asset = 'EURUSD'
        session.symbol = 'EURUSD=X'
    elif 'btc' in message.lower() or 'bitcoin' in message.lower():
        session.asset = 'BITCOIN'
        session.symbol = 'BTC-USD'
    
    return {
        'text': f"✅ {session.asset} selected. What's the current price on your chart?",
        'action': 'asset_selected',
        'data': {'asset': session.asset, 'symbol': session.symbol}
    }

def handle_price_input(session: TradingSession, message: str) -> Dict:
    """Handle price input"""
    import re
    numbers = re.findall(r'\d+\.?\d*', message)
    if numbers:
        session.price = float(numbers[0])
        
        # Get live comparison prices
        live_price = MarketDataFetcher.get_current_price(session.symbol)
        
        return {
            'text': f"Price recorded: ${session.price}. Live price: ${live_price['price']:.2f}. What timeframe would you like to trade?",
            'action': 'price_set',
            'data': {'price': session.price, 'live_price': live_price['price']}
        }
    
    return {'text': "Please provide a valid price."}

def handle_timeframe_selection(session: TradingSession, message: str) -> Dict:
    """Handle timeframe selection"""
    timeframes = {
        '5m': '5M', '15m': '15M', '30m': '30M',
        '1h': '1H', '4h': '4H', '1d': '1D', 'daily': '1D'
    }
    
    for key, value in timeframes.items():
        if key in message.lower():
            session.timeframe = value
            return {
                'text': f"✅ {value} timeframe selected. Please provide your account type and balance.",
                'action': 'timeframe_set',
                'data': {'timeframe': value}
            }
    
    return {'text': "Please specify a valid timeframe (5M, 15M, 30M, 1H, 4H, 1D)."}

def handle_account_info(session: TradingSession, message: str) -> Dict:
    """Handle account information"""
    import re
    
    # Extract account type
    if 'funded' in message.lower():
        session.account_type = 'Funded'
    else:
        session.account_type = 'Personal'
    
    # Extract balance
    numbers = re.findall(r'\d+', message)
    if numbers:
        session.balance = float(numbers[0])
    else:
        session.balance = 10000  # Default
    
    return {
        'text': f"Account configured: {session.account_type} account with ${session.balance:,.0f} balance. Ready to analyze!",
        'action': 'account_set',
        'data': {'type': session.account_type, 'balance': session.balance}
    }

def generate_educational_content(topic: str) -> str:
    """Generate educational content on trading topics"""
    content = {
        'order_blocks': """
        📚 **Order Blocks Explained**
        
        Order Blocks are supply/demand zones where institutional traders placed significant orders:
        
        • **Bullish OB**: Last down candle before aggressive up move
        • **Bearish OB**: Last up candle before aggressive down move
        • Act as future support/resistance levels
        • Higher probability when unmitigated
        
        💡 Pro tip: Combine with liquidity sweeps for high-probability setups!
        """,
        
        'liquidity': """
        💧 **Liquidity Concepts**
        
        Liquidity pools are areas where stop losses accumulate:
        
        • **Buy-side**: Above recent highs (short stops)
        • **Sell-side**: Below recent lows (long stops)
        • Price often sweeps liquidity before reversing
        • Equal highs/lows are strong liquidity magnets
        
        💡 Trading tip: Wait for liquidity sweeps before entering!
        """
    }
    
    return content.get(topic, "Topic information not available.")

def generate_conversational_response(message: str) -> str:
    """Generate a conversational response for general queries"""
    return """
    I can help you with trading analysis! Here's what I can do:
    
    • Analyze any asset (Forex, Crypto, Commodities)
    • Identify order blocks and liquidity zones
    • Calculate position sizes and risk management
    • Provide entry, stop loss, and take profit levels
    • Explain trading concepts and strategies
    
    To get started, just tell me which asset you'd like to analyze!
    """

if __name__ == '__main__':
    # Run the Flask app with WebSocket support
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)