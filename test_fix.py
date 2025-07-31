#!/usr/bin/env python3
"""
Test script to verify the bug fix for Horizon Exam Bot
Tests that essential dependencies can be imported and the Flask app can start
"""

import sys
import subprocess
import time
import requests
from threading import Thread

def test_dependencies():
    """Test that essential dependencies can be imported"""
    print("🧪 Testing essential dependencies...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError:
        print("❌ Flask import failed")
        return False
        
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError:
        print("❌ PyPDF2 import failed")
        return False
        
    try:
        from docx import Document
        print("✅ python-docx imported successfully")
    except ImportError:
        print("❌ python-docx import failed")
        return False
        
    return True

def test_app_import():
    """Test that the Flask app can be imported"""
    print("\n🧪 Testing Flask app import...")
    
    try:
        from app import app
        print("✅ Flask app imported successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        return False

def test_app_startup():
    """Test that the Flask app can start"""
    print("\n🧪 Testing Flask app startup...")
    
    # Start the app in a subprocess
    process = subprocess.Popen([sys.executable, "run.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    # Give it time to start
    time.sleep(3)
    
    try:
        # Test if the app is running
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask app started successfully")
            print("✅ Main page is accessible")
            success = True
        else:
            print(f"❌ App responded with status code: {response.status_code}")
            success = False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to app: {e}")
        success = False
    finally:
        # Clean up the process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    return success

def main():
    """Run all tests"""
    print("🔧 Testing Horizon Exam Bot Bug Fix")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: Dependencies
    if not test_dependencies():
        all_passed = False
    
    # Test 2: App import
    if not test_app_import():
        all_passed = False
    
    # Test 3: App startup
    if not test_app_startup():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Bug fix is successful!")
        print("✅ The application can now run with minimal dependencies")
        return 0
    else:
        print("❌ Some tests failed. Bug fix needs more work.")
        return 1

if __name__ == "__main__":
    sys.exit(main())