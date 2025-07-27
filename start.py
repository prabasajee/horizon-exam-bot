#!/usr/bin/env python3
"""
Production startup script for Horizon Exam Bot
This script configures the application for production deployment
"""

import os
import sys
from app import app

def main():
    """Main function to start the application in production mode"""
    
    # Set production defaults
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-in-production')
    app.config['FLASK_ENV'] = 'production'
    
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    print(f"🚀 Starting Horizon Exam Bot in production mode")
    print(f"🌐 Host: {host}:{port}")
    print(f"🔧 Debug: {debug}")
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    try:
        app.run(
            debug=debug,
            host=host,
            port=port,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()