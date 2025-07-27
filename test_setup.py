"""
Test script for Horizon Exam Bot functionality
Run this after installing dependencies to verify everything works
"""

import json
import os
import tempfile
from datetime import datetime

def test_document_processor():
    """Test document processing functionality"""
    try:
        from app import DocumentProcessor
        print("✅ DocumentProcessor imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import DocumentProcessor: {e}")
        return False

def test_quiz_manager():
    """Test quiz management functionality"""
    try:
        from app import QuizManager
        
        # Test quiz creation
        sample_quiz = {
            "title": "Test Quiz",
            "description": "A test quiz for verification",
            "questions": [
                {
                    "question": "What is 2 + 2?",
                    "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                    "correct_answer": "B",
                    "explanation": "Basic arithmetic: 2 + 2 = 4"
                }
            ]
        }
        
        # Save quiz
        quiz_id = QuizManager.save_quiz(sample_quiz)
        print(f"✅ Quiz saved with ID: {quiz_id}")
        
        # Load quiz
        loaded_quiz = QuizManager.load_quiz(quiz_id)
        print("✅ Quiz loaded successfully")
        
        # Test scoring
        user_answers = {"0": "B"}
        results = QuizManager.calculate_score(loaded_quiz, user_answers)
        print(f"✅ Scoring test: {results['score_percentage']}% (Expected: 100%)")
        
        # Clean up
        os.remove(f"data/quiz_{quiz_id}.json")
        print("✅ QuizManager tests passed")
        return True
        
    except Exception as e:
        print(f"❌ QuizManager test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization"""
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        # Test basic configuration
        assert app.config['UPLOAD_FOLDER'] == 'uploads'
        assert app.config['MAX_CONTENT_LENGTH'] == 16 * 1024 * 1024
        print("✅ Flask app configuration verified")
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_directories():
    """Test directory creation"""
    try:
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        
        # Check if files exist
        required_files = [
            'app.py',
            'requirements.txt',
            'templates/index.html',
            'templates/quiz.html',
            'templates/results.html'
        ]
        
        for file in required_files:
            if os.path.exists(file):
                print(f"✅ {file} exists")
            else:
                print(f"❌ {file} missing")
                return False
        
        print("✅ All required files and directories verified")
        return True
        
    except Exception as e:
        print(f"❌ Directory test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Horizon Exam Bot Setup")
    print("=" * 40)
    
    tests = [
        ("Directory Structure", test_directories),
        ("Flask App", test_flask_app),
        ("Document Processor", test_document_processor),
        ("Quiz Manager", test_quiz_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Horizon Exam Bot is ready to use!")
        print("🚀 Run 'python run.py' to start the application")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("💡 Make sure you've installed all dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
