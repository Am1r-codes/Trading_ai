from http.server import BaseHTTPRequestHandler
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import app

def handler(request):
    """Vercel serverless function handler"""
    return app(request, lambda: None) 