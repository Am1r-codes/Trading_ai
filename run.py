#!/usr/bin/env python3
"""
Trading Assistant Startup Script
Loads environment variables and starts the Flask application
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the Flask app
from trading_assistant_backend import app, socketio

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Trading Assistant on port {port}")
    print(f"📊 Backend URL: http://localhost:{port}")
    print(f"🌐 Frontend URL: http://localhost:8000")
    print(f"🔧 Debug mode: {debug}")
    print("\n" + "="*50)
    print("📋 Setup Instructions:")
    print("1. Copy env.example to .env and add your API keys")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Open frontend/index.html in your browser")
    print("="*50 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=debug) 