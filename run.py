"""
Simple run script for Horizon Exam Bot
Usage: python run.py
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Check if dependencies are installed
    try:
        import flask
        import PyPDF2
        import docx
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("🚀 Starting Horizon Exam Bot...")
    print("📚 Upload your lecture notes and create quizzes!")
    print("🌐 Access the application at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Horizon Exam Bot. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)
