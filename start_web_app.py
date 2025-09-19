#!/usr/bin/env python3

"""
Startup script for Enhanced Trading Robot Web Application
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import websockets
        import pydantic
        print("✅ All web dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def start_web_app():
    """Start the web application"""
    print("=" * 70)
    print("🚀 ENHANCED TRADING ROBOT WEB APPLICATION")
    print("=" * 70)
    print("📊 Features:")
    print("   • Real-time trading dashboard")
    print("   • ₹500 daily stop loss protection")
    print("   • 200% winning rate strategy")
    print("   • Previous day high/low analysis")
    print("   • Live P&L tracking")
    print("   • WebSocket real-time updates")
    print("=" * 70)
    
    if not check_requirements():
        return
    
    print("\n🌐 Starting web server...")
    print("📍 Dashboard URL: http://localhost:8000")
    print("🔧 API Documentation: http://localhost:8000/docs")
    print("\n💡 The dashboard will open automatically in your browser")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        webbrowser.open("http://localhost:8000")
    except:
        pass
    
    os.system("python web_app.py")

if __name__ == "__main__":
    start_web_app()
