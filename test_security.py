#!/usr/bin/env python3
"""
Security Tests for Horizon Exam Bot
Tests the security implementations and configurations
"""

import os
import sys
import requests
import json
import tempfile
from unittest.mock import patch
import subprocess


class SecurityTests:
    """Security test suite"""
    
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.tests_passed = 0
        self.tests_failed = 0
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🛡️ Running Security Tests for Horizon Exam Bot")
        print("=" * 50)
        
        # Configuration tests
        self.test_secret_key_configuration()
        self.test_session_security_configuration()
        self.test_debug_mode_configuration()
        
        # Application tests (require running app)
        print("\n📡 Testing Application Security (requires running app)...")
        try:
            self.test_security_headers()
            self.test_file_upload_validation()
            self.test_input_validation()
            self.test_error_handling()
        except requests.exceptions.ConnectionError:
            print("⚠️ Application not running - skipping runtime tests")
            print("💡 To test runtime security, start the app with: python run.py")
        
        # Report results
        self.report_results()
    
    def test_secret_key_configuration(self):
        """Test secret key configuration"""
        print("\n🔐 Testing Secret Key Configuration...")
        
        # Test environment variable support
        with patch.dict(os.environ, {'SECRET_KEY': 'test-secret-key'}):
            # Import app to test configuration
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            try:
                from app import app
                if app.config['SECRET_KEY'] == 'test-secret-key':
                    self.assert_test(True, "Environment variable SECRET_KEY is respected")
                else:
                    self.assert_test(False, "Environment variable SECRET_KEY not used")
            except Exception as e:
                self.assert_test(False, f"Error testing secret key config: {e}")
    
    def test_session_security_configuration(self):
        """Test session security configuration"""
        print("\n🍪 Testing Session Security Configuration...")
        
        try:
            from app import app
            
            # Test HttpOnly setting
            self.assert_test(
                app.config.get('SESSION_COOKIE_HTTPONLY', False),
                "SESSION_COOKIE_HTTPONLY is enabled"
            )
            
            # Test SameSite setting
            self.assert_test(
                app.config.get('SESSION_COOKIE_SAMESITE') == 'Lax',
                "SESSION_COOKIE_SAMESITE is set to Lax"
            )
            
        except Exception as e:
            self.assert_test(False, f"Error testing session config: {e}")
    
    def test_debug_mode_configuration(self):
        """Test debug mode configuration"""
        print("\n🐛 Testing Debug Mode Configuration...")
        
        # Test with production environment
        with patch.dict(os.environ, {'FLASK_DEBUG': 'False', 'FLASK_ENV': 'production'}):
            try:
                from app import app
                # App should not be in debug mode in production
                self.assert_test(
                    not app.debug,
                    "Debug mode is disabled in production environment"
                )
            except Exception as e:
                self.assert_test(False, f"Error testing debug config: {e}")
    
    def test_security_headers(self):
        """Test security headers implementation"""
        print("\n🛡️ Testing Security Headers...")
        
        try:
            response = requests.get(self.base_url, timeout=5)
            headers = response.headers
            
            # Test required security headers
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Content-Security-Policy': lambda v: 'default-src' in v,
                'Referrer-Policy': 'strict-origin-when-cross-origin'
            }
            
            for header, expected in required_headers.items():
                if header in headers:
                    if callable(expected):
                        if expected(headers[header]):
                            self.assert_test(True, f"Security header {header} is properly configured")
                        else:
                            self.assert_test(False, f"Security header {header} has incorrect value")
                    else:
                        if headers[header] == expected:
                            self.assert_test(True, f"Security header {header} is properly set")
                        else:
                            self.assert_test(False, f"Security header {header} has incorrect value")
                else:
                    self.assert_test(False, f"Security header {header} is missing")
        
        except Exception as e:
            self.assert_test(False, f"Error testing security headers: {e}")
    
    def test_file_upload_validation(self):
        """Test file upload security validation"""
        print("\n📁 Testing File Upload Security...")
        
        try:
            # Test file type validation
            test_data = "This is a test file content"
            
            # Test invalid file type
            files = {'file': ('test.txt', test_data, 'text/plain')}
            response = requests.post(f"{self.base_url}/api/upload", files=files, timeout=10)
            
            if response.status_code == 400:
                self.assert_test(True, "Invalid file types are rejected")
            else:
                self.assert_test(False, "Invalid file types are not properly rejected")
            
            # Test missing file
            response = requests.post(f"{self.base_url}/api/upload", timeout=10)
            
            if response.status_code == 400:
                self.assert_test(True, "Missing file uploads are rejected")
            else:
                self.assert_test(False, "Missing file uploads are not properly handled")
        
        except Exception as e:
            self.assert_test(False, f"Error testing file upload validation: {e}")
    
    def test_input_validation(self):
        """Test input validation for JSON endpoints"""
        print("\n✅ Testing Input Validation...")
        
        try:
            # Test quiz creation with invalid data
            invalid_data = {"invalid": "data"}
            response = requests.post(
                f"{self.base_url}/api/quiz/create",
                json=invalid_data,
                timeout=10
            )
            
            if response.status_code == 400:
                self.assert_test(True, "Invalid quiz creation data is rejected")
            else:
                self.assert_test(False, "Invalid quiz creation data is not properly validated")
            
            # Test quiz submission with invalid ID
            response = requests.post(
                f"{self.base_url}/api/quiz/invalid-id/submit",
                json={"answers": {}},
                timeout=10
            )
            
            if response.status_code == 400:
                self.assert_test(True, "Invalid quiz IDs are rejected")
            else:
                self.assert_test(False, "Invalid quiz IDs are not properly validated")
        
        except Exception as e:
            self.assert_test(False, f"Error testing input validation: {e}")
    
    def test_error_handling(self):
        """Test error handling for information disclosure"""
        print("\n🚨 Testing Error Handling...")
        
        try:
            # Test non-existent quiz
            response = requests.get(f"{self.base_url}/api/quiz/nonexistent-uuid", timeout=10)
            
            if response.status_code == 404:
                data = response.json()
                # Check that error message doesn't expose internal details
                if 'error' in data and 'Server error' not in data['error']:
                    self.assert_test(True, "Generic error messages are used")
                else:
                    self.assert_test(False, "Error messages may expose internal details")
            else:
                self.assert_test(False, "Non-existent resources don't return proper 404")
        
        except Exception as e:
            self.assert_test(False, f"Error testing error handling: {e}")
    
    def assert_test(self, condition, message):
        """Assert a test condition"""
        if condition:
            print(f"✅ {message}")
            self.tests_passed += 1
        else:
            print(f"❌ {message}")
            self.tests_failed += 1
    
    def report_results(self):
        """Report test results"""
        print("\n" + "=" * 50)
        print("🏁 Security Test Results")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"📊 Total Tests: {self.tests_passed + self.tests_failed}")
        
        if self.tests_failed == 0:
            print("\n🎉 All security tests passed!")
            return True
        else:
            print(f"\n⚠️ {self.tests_failed} security tests failed!")
            print("🔧 Please review and fix the failed security checks.")
            return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run security tests for Horizon Exam Bot")
    parser.add_argument("--url", default="http://127.0.0.1:5000", 
                       help="Base URL of the application (default: http://127.0.0.1:5000)")
    
    args = parser.parse_args()
    
    tester = SecurityTests(args.url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()