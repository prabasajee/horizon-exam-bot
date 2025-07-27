"""
Performance and Security Improvements for Horizon Exam Bot
Includes caching, rate limiting, security measures, and optimization
"""

from flask import request, jsonify, g
from functools import wraps
import time
import hashlib
import redis
import logging
from datetime import datetime, timedelta
import secrets
import jwt
from werkzeug.security import check_password_hash
import bleach
import re
from typing import Dict, Any, Optional
import os

class CacheManager:
    """Redis-based caching system for improved performance"""
    
    def __init__(self, redis_url='redis://localhost:6379'):
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()  # Test connection
            self.enabled = True
        except:
            self.redis_client = None
            self.enabled = False
            logging.warning("Redis not available, caching disabled")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value.decode('utf-8'))
        except Exception as e:
            logging.error(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, expiry: int = 3600) -> bool:
        """Set value in cache with expiry (seconds)"""
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            return self.redis_client.setex(key, expiry, serialized)
        except Exception as e:
            logging.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logging.error(f"Cache delete error: {e}")
            return False
    
    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            logging.error(f"Cache flush error: {e}")
        
        return 0

class RateLimiter:
    """Rate limiting to prevent abuse"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    def is_allowed(self, identifier: str, limit: int, window: int) -> bool:
        """Check if request is allowed within rate limit"""
        key = f"rate_limit:{identifier}:{int(time.time() // window)}"
        
        try:
            current = self.cache.get(key) or 0
            if current >= limit:
                return False
            
            # Increment counter
            self.cache.set(key, current + 1, window)
            return True
        except:
            # If cache fails, allow request (fail open)
            return True
    
    def get_remaining(self, identifier: str, limit: int, window: int) -> int:
        """Get remaining requests in current window"""
        key = f"rate_limit:{identifier}:{int(time.time() // window)}"
        current = self.cache.get(key) or 0
        return max(0, limit - current)

class SecurityManager:
    """Comprehensive security measures"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.jwt_algorithm = 'HS256'
        self.token_expiry = 24 * 60 * 60  # 24 hours
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token: str, session_token: str) -> bool:
        """Validate CSRF token"""
        return secrets.compare_digest(token, session_token)
    
    def generate_jwt_token(self, user_id: int, additional_claims: Dict = None) -> str:
        """Generate JWT token for authentication"""
        payload = {
            'user_id': user_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry)
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
    
    def validate_jwt_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def sanitize_input(self, text: str, allow_html: bool = False) -> str:
        """Sanitize user input to prevent XSS"""
        if not allow_html:
            # Strip all HTML tags
            return bleach.clean(text, tags=[], strip=True)
        else:
            # Allow safe HTML tags only
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3']
            return bleach.clean(text, tags=allowed_tags, strip=True)
    
    def validate_file_upload(self, file) -> Dict[str, Any]:
        """Validate uploaded file for security"""
        if not file or not file.filename:
            return {'valid': False, 'error': 'No file provided'}
        
        # Check file extension
        allowed_extensions = {'.pdf', '.docx', '.txt', '.doc'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return {'valid': False, 'error': 'File type not allowed'}
        
        # Check file size (16MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 16 * 1024 * 1024:
            return {'valid': False, 'error': 'File too large (max 16MB)'}
        
        # Check filename for suspicious patterns
        if self.has_suspicious_filename(file.filename):
            return {'valid': False, 'error': 'Invalid filename'}
        
        return {'valid': True}
    
    def has_suspicious_filename(self, filename: str) -> bool:
        """Check for suspicious filename patterns"""
        suspicious_patterns = [
            r'\.\./',  # Directory traversal
            r'[<>:"|?*]',  # Invalid filename characters
            r'^\.',  # Hidden files
            r'\.exe$|\.bat$|\.cmd$|\.scr$|\.com$'  # Executable files
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        
        return False
    
    def hash_password(self, password: str, salt: str = None) -> Dict[str, str]:
        """Hash password with salt"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)  # 100k iterations
        
        return {
            'hash': password_hash.hex(),
            'salt': salt
        }
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        new_hash = self.hash_password(password, salt)['hash']
        return secrets.compare_digest(new_hash, stored_hash)

class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    def cache_quiz_data(self, quiz_id: str, quiz_data: Dict, expiry: int = 3600):
        """Cache quiz data for faster access"""
        cache_key = f"quiz_data:{quiz_id}"
        self.cache.set(cache_key, quiz_data, expiry)
    
    def get_cached_quiz(self, quiz_id: str) -> Optional[Dict]:
        """Get cached quiz data"""
        cache_key = f"quiz_data:{quiz_id}"
        return self.cache.get(cache_key)
    
    def cache_user_stats(self, user_id: int, stats: Dict, expiry: int = 1800):
        """Cache user statistics"""
        cache_key = f"user_stats:{user_id}"
        self.cache.set(cache_key, stats, expiry)
    
    def get_cached_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get cached user statistics"""
        cache_key = f"user_stats:{user_id}"
        return self.cache.get(cache_key)
    
    def invalidate_user_cache(self, user_id: int):
        """Invalidate all cache entries for a user"""
        patterns = [
            f"user_stats:{user_id}",
            f"user_quizzes:{user_id}",
            f"user_notes:{user_id}"
        ]
        
        for pattern in patterns:
            self.cache.delete(pattern)
    
    def preload_popular_content(self):
        """Preload frequently accessed content"""
        # This would query the database for popular quizzes and cache them
        pass

# Decorators for security and performance
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        security_manager = SecurityManager(os.getenv('SECRET_KEY', 'dev-key'))
        payload = security_manager.validate_jwt_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        g.current_user_id = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit(limit: int = 100, window: int = 3600):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP or user ID)
            identifier = request.remote_addr
            if hasattr(g, 'current_user_id'):
                identifier = f"user:{g.current_user_id}"
            
            cache_manager = CacheManager()
            rate_limiter = RateLimiter(cache_manager)
            
            if not rate_limiter.is_allowed(identifier, limit, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': window
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def cache_response(expiry: int = 3600, key_prefix: str = None):
    """Decorator to cache API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_key = key_prefix or f.__name__
            if args:
                cache_key += f":{':'.join(map(str, args))}"
            if request.args:
                cache_key += f":{hashlib.md5(str(sorted(request.args.items())).encode()).hexdigest()}"
            
            cache_manager = CacheManager()
            
            # Try to get from cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                return jsonify(cached_result)
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            
            # Only cache successful responses
            if hasattr(result, 'status_code') and result.status_code == 200:
                cache_manager.set(cache_key, result.get_json(), expiry)
            
            return result
        
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
            
            # Basic validation
            for field, rules in schema.items():
                if rules.get('required', False) and field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
                
                if field in data:
                    value = data[field]
                    
                    # Type validation
                    if 'type' in rules and not isinstance(value, rules['type']):
                        return jsonify({'error': f'Invalid type for field: {field}'}), 400
                    
                    # Length validation for strings
                    if isinstance(value, str) and 'max_length' in rules:
                        if len(value) > rules['max_length']:
                            return jsonify({'error': f'Field {field} too long'}), 400
                    
                    # Sanitize string inputs
                    if isinstance(value, str):
                        security_manager = SecurityManager(os.getenv('SECRET_KEY', 'dev-key'))
                        data[field] = security_manager.sanitize_input(value)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Logging and monitoring
class SecurityLogger:
    """Security event logging"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_failed_login(self, username: str, ip: str):
        """Log failed login attempt"""
        self.logger.warning(f"Failed login attempt - Username: {username}, IP: {ip}")
    
    def log_suspicious_activity(self, user_id: int, activity: str, details: str):
        """Log suspicious activity"""
        self.logger.warning(f"Suspicious activity - User: {user_id}, Activity: {activity}, Details: {details}")
    
    def log_successful_login(self, user_id: int, ip: str):
        """Log successful login"""
        self.logger.info(f"Successful login - User: {user_id}, IP: {ip}")
    
    def log_file_upload(self, user_id: int, filename: str, size: int):
        """Log file upload"""
        self.logger.info(f"File upload - User: {user_id}, File: {filename}, Size: {size}")

# Database connection pooling
class DatabasePool:
    """Simple database connection pooling"""
    
    def __init__(self, db_path: str, pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections = []
        self.in_use = set()
    
    def get_connection(self):
        """Get database connection from pool"""
        # Simplified implementation - in production use proper pooling library
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def return_connection(self, conn):
        """Return connection to pool"""
        # In a real implementation, you'd return to pool
        conn.close()

# Error handling and monitoring
class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self):
        self.logger = logging.getLogger('errors')
        self.logger.setLevel(logging.ERROR)
        
        handler = logging.FileHandler('logs/errors.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_error(self, error: Exception, context: Dict = None):
        """Log error with context"""
        error_msg = f"Error: {str(error)}"
        if context:
            error_msg += f" - Context: {context}"
        
        self.logger.error(error_msg, exc_info=True)
    
    def handle_api_error(self, error: Exception, endpoint: str) -> Dict[str, Any]:
        """Handle API errors and return standardized response"""
        self.log_error(error, {'endpoint': endpoint})
        
        # Don't expose internal errors in production
        if os.getenv('FLASK_ENV') == 'production':
            return {
                'error': 'Internal server error',
                'error_id': secrets.token_hex(8)
            }
        else:
            return {
                'error': str(error),
                'type': type(error).__name__
            }

# Health check endpoint
def health_check() -> Dict[str, Any]:
    """System health check"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'components': {}
    }
    
    # Check database
    try:
        import sqlite3
        conn = sqlite3.connect('horizon_exam.db')
        conn.execute('SELECT 1')
        conn.close()
        health_status['components']['database'] = 'healthy'
    except Exception as e:
        health_status['components']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check cache
    try:
        cache = CacheManager()
        if cache.enabled:
            cache.set('health_check', 'ok', 60)
            health_status['components']['cache'] = 'healthy'
        else:
            health_status['components']['cache'] = 'disabled'
    except Exception as e:
        health_status['components']['cache'] = f'unhealthy: {str(e)}'
    
    return health_status
