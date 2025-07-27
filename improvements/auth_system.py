"""
Enhanced User Authentication System for Horizon Exam Bot
Includes login, registration, password reset, and role-based access
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import re
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MimeText

auth_bp = Blueprint('auth', __name__)

class UserManager:
    def __init__(self, db_path='horizon_exam.db'):
        self.db_path = db_path
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def register_user(self, username, email, password, first_name='', last_name=''):
        """Register a new user"""
        try:
            # Validate input
            if not self.validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}
            
            if not self.validate_password(password):
                return {'success': False, 'error': 'Password must be at least 8 characters with uppercase, lowercase, and number'}
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                return {'success': False, 'error': 'Username or email already exists'}
            
            # Create user
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, first_name, last_name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id, 'message': 'User registered successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Find user by username or email
            cursor.execute('''
                SELECT id, username, email, password_hash, first_name, last_name, role
                FROM users WHERE username = ? OR email = ?
            ''', (username, username))
            
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                # Update last login
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                             (datetime.now().isoformat(), user['id']))
                conn.commit()
                conn.close()
                
                return {
                    'success': True,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'first_name': user['first_name'],
                        'last_name': user['last_name'],
                        'role': user['role']
                    }
                }
            else:
                conn.close()
                return {'success': False, 'error': 'Invalid credentials'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_by_id(self, user_id):
        """Get user information by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, first_name, last_name, role, created_at, last_login
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'success': True,
                    'user': dict(user)
                }
            else:
                return {'success': False, 'error': 'User not found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_user_profile(self, user_id, **kwargs):
        """Update user profile information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            fields = []
            values = []
            
            for field in ['first_name', 'last_name', 'email']:
                if field in kwargs and kwargs[field] is not None:
                    fields.append(f"{field} = ?")
                    values.append(kwargs[field])
            
            if not fields:
                return {'success': False, 'error': 'No fields to update'}
            
            values.append(user_id)
            
            cursor.execute(f'''
                UPDATE users SET {', '.join(fields)}
                WHERE id = ?
            ''', values)
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Profile updated successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def change_password(self, user_id, current_password, new_password):
        """Change user password"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verify current password
            cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user or not check_password_hash(user['password_hash'], current_password):
                conn.close()
                return {'success': False, 'error': 'Current password is incorrect'}
            
            # Validate new password
            if not self.validate_password(new_password):
                conn.close()
                return {'success': False, 'error': 'New password does not meet requirements'}
            
            # Update password
            new_password_hash = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                         (new_password_hash, user_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        """Validate password strength"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_manager = UserManager()
        user_data = user_manager.get_user_by_id(session['user_id'])
        
        if not user_data['success'] or user_data['user']['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    data = request.get_json()
    user_manager = UserManager()
    
    result = user_manager.register_user(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password'),
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', '')
    )
    
    return jsonify(result)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    data = request.get_json()
    user_manager = UserManager()
    
    result = user_manager.authenticate_user(
        username=data.get('username'),
        password=data.get('password')
    )
    
    if result['success']:
        session['user_id'] = result['user']['id']
        session['username'] = result['user']['username']
        session['role'] = result['user']['role']
    
    return jsonify(result)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/profile')
@login_required
def profile():
    user_manager = UserManager()
    result = user_manager.get_user_by_id(session['user_id'])
    
    if result['success']:
        return render_template('auth/profile.html', user=result['user'])
    else:
        return jsonify(result), 404

@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    user_manager = UserManager()
    
    result = user_manager.update_user_profile(
        user_id=session['user_id'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email')
    )
    
    return jsonify(result)

@auth_bp.route('/password/change', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    user_manager = UserManager()
    
    result = user_manager.change_password(
        user_id=session['user_id'],
        current_password=data.get('current_password'),
        new_password=data.get('new_password')
    )
    
    return jsonify(result)

@auth_bp.route('/users')
@admin_required
def list_users():
    """Admin route to list all users"""
    try:
        user_manager = UserManager()
        conn = user_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, first_name, last_name, role, created_at, last_login
            FROM users ORDER BY created_at DESC
        ''')
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'success': True, 'users': users})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
