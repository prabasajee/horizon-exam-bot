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
        # Check environment for configuration
        debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'  # Default to True for development
        host = os.environ.get('FLASK_HOST', '127.0.0.1')  # More secure default
        port = int(os.environ.get('FLASK_PORT', '5000'))
        
        app.run(
            debug=debug_mode,
            host=host,
            port=port,
            use_reloader=debug_mode
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Horizon Exam Bot. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)
