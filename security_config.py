"""
Security Configuration and Utilities for Horizon Exam Bot
Centralized security settings and validation functions
"""

import os
import re
import html
import secrets
import hashlib
import logging
from typing import Dict, List, Any, Optional
from functools import wraps
from flask import request, jsonify, g
import time

class SecurityConfig:
    """Centralized security configuration"""
    
    # File upload settings
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    MAX_FILENAME_LENGTH = 255
    
    # Input validation settings
    MAX_TEXT_LENGTH = 100000
    MAX_TITLE_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_QUESTION_LENGTH = 1000
    MAX_OPTION_LENGTH = 500
    MAX_QUESTIONS_PER_QUIZ = 50
    MAX_OPTIONS_PER_QUESTION = 6
    MIN_OPTIONS_PER_QUESTION = 2
    MIN_TEXT_LENGTH_FOR_NOTES = 100
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = SecurityConfig.MAX_TEXT_LENGTH) -> str:
        """Sanitize text input to prevent XSS and other attacks"""
        if not isinstance(text, str):
            return ""
        
        # Limit length to prevent DoS
        if len(text) > max_length:
            text = text[:max_length]
        
        # HTML escape to prevent XSS
        text = html.escape(text, quote=True)
        
        # Remove potentially dangerous characters but preserve basic punctuation
        text = re.sub(r'[<>"\';`]', '', text)
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        return text.strip()
    
    @staticmethod
    def validate_filename(filename: str) -> Dict[str, Any]:
        """Validate filename for security"""
        result = {'valid': True, 'error': ''}
        
        if not filename:
            result['valid'] = False
            result['error'] = 'Filename is required'
            return result
        
        # Check length
        if len(filename) > SecurityConfig.MAX_FILENAME_LENGTH:
            result['valid'] = False
            result['error'] = 'Filename too long'
            return result
        
        # Check for directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            result['valid'] = False
            result['error'] = 'Invalid filename characters'
            return result
        
        # Check for suspicious extensions
        suspicious_extensions = {
            '.exe', '.bat', '.cmd', '.scr', '.com', '.pif', '.jar', 
            '.js', '.vbs', '.ps1', '.php', '.asp', '.jsp'
        }
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in suspicious_extensions:
            result['valid'] = False
            result['error'] = 'File type not allowed'
            return result
        
        # Check if extension is in allowed list
        if file_ext.lstrip('.') not in SecurityConfig.ALLOWED_EXTENSIONS:
            result['valid'] = False
            result['error'] = f'Only {", ".join(SecurityConfig.ALLOWED_EXTENSIONS)} files are allowed'
            return result
        
        return result
    
    @staticmethod
    def validate_json_structure(data: Any, required_fields: List[str], max_fields: int = 20) -> Dict[str, Any]:
        """Validate JSON input structure"""
        result = {'valid': True, 'errors': []}
        
        if not isinstance(data, dict):
            result['valid'] = False
            result['errors'].append('Invalid data format - expected JSON object')
            return result
        
        # Check for too many fields (DoS protection)
        if len(data) > max_fields:
            result['valid'] = False
            result['errors'].append(f'Too many fields (maximum {max_fields})')
            return result
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                result['valid'] = False
                result['errors'].append(f'Missing required field: {field}')
        
        return result
    
    @staticmethod
    def validate_quiz_data(quiz_data: Dict) -> Dict[str, Any]:
        """Validate quiz data structure and content"""
        result = {'valid': True, 'errors': []}
        
        # Validate title
        if 'title' not in quiz_data or not quiz_data['title'].strip():
            result['valid'] = False
            result['errors'].append('Title is required')
        elif len(quiz_data['title']) > SecurityConfig.MAX_TITLE_LENGTH:
            result['valid'] = False
            result['errors'].append(f'Title too long (maximum {SecurityConfig.MAX_TITLE_LENGTH} characters)')
        
        # Validate questions
        if 'questions' not in quiz_data:
            result['valid'] = False
            result['errors'].append('Questions are required')
        else:
            questions = quiz_data['questions']
            if not isinstance(questions, list):
                result['valid'] = False
                result['errors'].append('Questions must be a list')
            elif len(questions) == 0:
                result['valid'] = False
                result['errors'].append('At least one question is required')
            elif len(questions) > SecurityConfig.MAX_QUESTIONS_PER_QUIZ:
                result['valid'] = False
                result['errors'].append(f'Too many questions (maximum {SecurityConfig.MAX_QUESTIONS_PER_QUIZ})')
            else:
                # Validate each question
                for i, question in enumerate(questions):
                    question_errors = InputValidator._validate_single_question(question, i + 1)
                    result['errors'].extend(question_errors)
                    if question_errors:
                        result['valid'] = False
        
        return result
    
    @staticmethod
    def _validate_single_question(question: Dict, question_num: int) -> List[str]:
        """Validate a single question"""
        errors = []
        
        if not isinstance(question, dict):
            errors.append(f'Question {question_num} has invalid format')
            return errors
        
        # Check required fields
        required_fields = ['question', 'options', 'correct_answer']
        for field in required_fields:
            if field not in question:
                errors.append(f'Question {question_num} missing field: {field}')
        
        # Validate question text
        if 'question' in question:
            if not question['question'].strip():
                errors.append(f'Question {question_num} text is empty')
            elif len(question['question']) > SecurityConfig.MAX_QUESTION_LENGTH:
                errors.append(f'Question {question_num} text too long')
        
        # Validate options
        if 'options' in question:
            options = question['options']
            if not isinstance(options, list):
                errors.append(f'Question {question_num} options must be a list')
            elif len(options) < SecurityConfig.MIN_OPTIONS_PER_QUESTION:
                errors.append(f'Question {question_num} needs at least {SecurityConfig.MIN_OPTIONS_PER_QUESTION} options')
            elif len(options) > SecurityConfig.MAX_OPTIONS_PER_QUESTION:
                errors.append(f'Question {question_num} has too many options (maximum {SecurityConfig.MAX_OPTIONS_PER_QUESTION})')
            else:
                for j, option in enumerate(options):
                    if not str(option).strip():
                        errors.append(f'Question {question_num} option {j + 1} is empty')
                    elif len(str(option)) > SecurityConfig.MAX_OPTION_LENGTH:
                        errors.append(f'Question {question_num} option {j + 1} too long')
        
        # Validate correct answer
        if 'correct_answer' in question:
            if not question['correct_answer'].strip():
                errors.append(f'Question {question_num} correct answer is empty')
            elif len(question['correct_answer']) > SecurityConfig.MAX_OPTION_LENGTH:
                errors.append(f'Question {question_num} correct answer too long')
        
        return errors

class SecurityLogger:
    """Security event logging"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Create file handler if not exists
        if not self.logger.handlers:
            handler = logging.FileHandler('logs/security.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_suspicious_activity(self, activity: str, details: str, ip: str = None):
        """Log suspicious activity"""
        ip_info = f" from {ip}" if ip else ""
        self.logger.warning(f"Suspicious activity: {activity} - {details}{ip_info}")
    
    def log_file_upload(self, filename: str, size: int, ip: str = None):
        """Log file upload"""
        ip_info = f" from {ip}" if ip else ""
        self.logger.info(f"File uploaded: {filename} ({size} bytes){ip_info}")
    
    def log_validation_error(self, error_type: str, details: str, ip: str = None):
        """Log validation errors"""
        ip_info = f" from {ip}" if ip else ""
        self.logger.warning(f"Validation error: {error_type} - {details}{ip_info}")

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, identifier: str, limit: int = SecurityConfig.RATE_LIMIT_REQUESTS, 
                  window: int = SecurityConfig.RATE_LIMIT_WINDOW) -> bool:
        """Check if request is allowed within rate limit"""
        current_time = int(time.time())
        window_start = current_time - (current_time % window)
        key = f"{identifier}:{window_start}"
        
        if key not in self.requests:
            self.requests[key] = 0
        
        # Clean old entries
        self._cleanup_old_entries(current_time, window)
        
        if self.requests[key] >= limit:
            return False
        
        self.requests[key] += 1
        return True
    
    def _cleanup_old_entries(self, current_time: int, window: int):
        """Remove old rate limit entries"""
        cutoff_time = current_time - window
        keys_to_remove = []
        
        for key in self.requests:
            if ':' in key:
                window_start = int(key.split(':')[1])
                if window_start < cutoff_time:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]

# Global instances
security_logger = SecurityLogger()
rate_limiter = RateLimiter()

# Decorators
def rate_limit(limit: int = SecurityConfig.RATE_LIMIT_REQUESTS, 
               window: int = SecurityConfig.RATE_LIMIT_WINDOW):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as identifier
            identifier = request.remote_addr or 'unknown'
            
            if not rate_limiter.is_allowed(identifier, limit, window):
                security_logger.log_suspicious_activity(
                    'Rate limit exceeded',
                    f'Endpoint: {request.endpoint}',
                    identifier
                )
                return jsonify({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': window
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def validate_input(schema: Dict):
    """Decorator to validate input against schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'error': 'JSON data required'}), 400
            
            # Validate structure
            validation_result = InputValidator.validate_json_structure(
                data, 
                schema.get('required_fields', []),
                schema.get('max_fields', 20)
            )
            
            if not validation_result['valid']:
                security_logger.log_validation_error(
                    'JSON structure validation',
                    f"Errors: {validation_result['errors']}",
                    request.remote_addr
                )
                return jsonify({'error': validation_result['errors'][0]}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator