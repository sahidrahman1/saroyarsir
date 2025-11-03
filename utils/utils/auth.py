"""
Authentication Utilities
Decorators and helper functions for authentication and authorization
"""
from functools import wraps
from flask import session, jsonify, request
from models import User, UserRole
import bcrypt

def generate_password_hash(password):
    """Generate password hash using bcrypt"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

def check_password_hash(hashed_password, password):
    """Check if password matches hash"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password, hashed_password)

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Authentication required', 'success': False}), 401
        
        # Check if user still exists and is active
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            return jsonify({'error': 'Invalid session', 'success': False}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(*allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_role = session.get('user_role')
            
            if not user_role:
                return jsonify({'error': 'Role information missing', 'success': False}), 401
            
            # Convert string to UserRole enum if needed
            if isinstance(user_role, str):
                try:
                    user_role = UserRole(user_role)
                except ValueError:
                    return jsonify({'error': 'Invalid role', 'success': False}), 401
            
            if user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions', 'success': False}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def get_current_user():
    """Get current user from session"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def get_current_user_id():
    """Get current user ID from session"""
    return session.get('user_id')

def get_current_user_role():
    """Get current user role from session"""
    user_role = session.get('user_role')
    if user_role and isinstance(user_role, str):
        try:
            return UserRole(user_role)
        except ValueError:
            return None
    return user_role

def is_teacher_or_admin():
    """Check if current user is teacher or super user"""
    user_role = get_current_user_role()
    return user_role in [UserRole.TEACHER, UserRole.SUPER_USER]

def is_admin():
    """Check if current user is super user"""
    user_role = get_current_user_role()
    return user_role == UserRole.SUPER_USER

def is_student():
    """Check if current user is student"""
    user_role = get_current_user_role()
    return user_role == UserRole.STUDENT

def check_batch_access(user, batch_id):
    """Check if user has access to a specific batch"""
    if is_admin():
        return True
    
    if is_teacher_or_admin():
        return True  # Teachers can access all batches
    
    if is_student():
        # Students can only access their enrolled batches
        user_batch_ids = [batch.id for batch in user.batches if batch.is_active]
        return int(batch_id) in user_batch_ids
    
    return False

def check_user_access(current_user, target_user_id):
    """Check if current user can access target user's data"""
    if is_admin():
        return True
    
    if is_teacher_or_admin():
        return True  # Teachers can access all students
    
    if is_student():
        # Students can only access their own data
        return current_user.id == int(target_user_id)
    
    return False