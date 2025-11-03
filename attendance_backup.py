"""
Authentication Routes
Login, logout, and session management
"""
from flask import Blueprint, request, jsonify, session
from flask_bcrypt import check_password_hash, generate_password_hash
from models import db, User, UserRole
from utils.auth import login_required, require_role
from utils.response import success_response, error_response
import re
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def validate_phone(phone):
    """Validate Bangladeshi phone number format"""
    # Remove any spaces or special characters
    phone = re.sub(r'[^\d]', '', phone)
    
    # Check if it's a valid Bangladeshi number
    if phone.startswith('880'):
        phone = phone[3:]  # Remove country code
    elif phone.startswith('+880'):
        phone = phone[4:]  # Remove country code with +
    
    # Should be 11 digits starting with 01
    if len(phone) == 11 and phone.startswith('01'):
        return phone
    
    return None

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint for all user types"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Support both phoneNumber (frontend) and phone (legacy)
        phone = data.get('phoneNumber') or data.get('phone')
        password = data.get('password')
        
        if not phone or not password:
            return error_response('Phone number and password are required', 400)
        
        # Validate and format phone number
        formatted_phone = validate_phone(phone)
        if not formatted_phone:
            return error_response('Invalid phone number format', 400)
        
        # Find user by phone
        user = User.query.filter_by(phoneNumber=formatted_phone).first()
        
        if not user:
            return error_response('Invalid phone number or password', 401)
        
        if not user.is_active:
            return error_response('Account is deactivated', 401)
        
        # Check password based on user role
        password_valid = False
        
        if user.role == UserRole.STUDENT:
            # For students, check if password matches last 4 digits of phone
            last_4_digits = formatted_phone[-4:]
            password_valid = (password == last_4_digits)
        else:
            # For teachers and super users, check hashed password
            if user.password_hash:
                password_valid = check_password_hash(user.password_hash, password)
        
        if not password_valid:
            return error_response('Invalid phone number or password', 401)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create session (match TypeScript session structure)
        session_user = {
            'id': user.id,
            'role': user.role.value,
            'name': f"{user.first_name} {user.last_name}",
            'firstName': user.first_name,
            'lastName': user.last_name,
            'phoneNumber': user.phoneNumber,
            'email': user.email,
            'smsCount': user.sms_count,
            'batchId': user.batches[0].id if user.batches and user.role == UserRole.STUDENT else None
        }
        
        # Set session data for both template and API compatibility
        session['user'] = session_user
        session['user_id'] = user.id
        session['user_role'] = user.role.value
        session.permanent = True
        
        # Prepare user data for response
        user_data = {
            'id': user.id,
            'phoneNumber': user.phoneNumber,  # Match frontend expectation
            'firstName': user.first_name,     # Match frontend expectation
            'lastName': user.last_name,       # Match frontend expectation
            'name': f"{user.first_name} {user.last_name}",  # Full name for session
            'email': user.email,
            'role': user.role.value,
            'profileImage': user.profile_image,
            'smsCount': user.sms_count,
            'lastLogin': user.last_login.isoformat() if user.last_login else None,
            'createdAt': user.created_at.isoformat()
        }
        
        # Add role-specific data
        if user.role == UserRole.STUDENT:
            # Get student's batches
            batches = [{
                'id': batch.id,
                'name': batch.name,
                'description': batch.description,
                'fee_amount': float(batch.fee_amount),
                'is_active': batch.is_active
            } for batch in user.batches if batch.is_active]
            
            user_data['batches'] = batches
        
        return success_response(
            'Login successful',
            {'success': True, 'user': session_user}
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Login failed: {str(e)}', 500)

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout endpoint"""
    try:
        user_id = session.get('user_id')
        
        # Clear session
        session.clear()
        
        return success_response('Logout successful')
        
    except Exception as e:
        return error_response(f'Logout failed: {str(e)}', 500)

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        user_data = {
            'id': user.id,
            'phoneNumber': user.phoneNumber,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'role': user.role.value,
            'profileImage': user.profile_image,
            'smsCount': user.sms_count,
            'lastLogin': user.last_login.isoformat() if user.last_login else None,
            'createdAt': user.created_at.isoformat()
        }
        
        # Add role-specific data
        if user.role == UserRole.STUDENT:
            # Get student's batches
            batches = [{
                'id': batch.id,
                'name': batch.name,
                'description': batch.description,
                'fee_amount': float(batch.fee_amount),
                'is_active': batch.is_active
            } for batch in user.batches if batch.is_active]
            
            user_data['batches'] = batches
        
        return success_response('User data retrieved', user_data)
        
    except Exception as e:
        return error_response(f'Failed to get user data: {str(e)}', 500)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password (for teachers and super users only)"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        if user.role == UserRole.STUDENT:
            return error_response('Students cannot change password', 403)
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return error_response('Current password and new password are required', 400)
        
        # Verify current password
        if not user.password_hash or not check_password_hash(user.password_hash, current_password):
            return error_response('Current password is incorrect', 401)
        
        # Validate new password
        if len(new_password) < 6:
            return error_response('New password must be at least 6 characters long', 400)
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response('Password changed successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to change password: {str(e)}', 500)

@auth_bp.route('/session-check', methods=['GET'])
def check_session():
    """Check if user session is valid"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return error_response('No active session', 401)
        
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            session.clear()
            return error_response('Invalid session', 401)
        
        return success_response('Session is valid', {
            'user_id': user_id,
            'user_role': session.get('user_role'),
            'user_name': session.get('user_name')
        })
        
    except Exception as e:
        return error_response(f'Session check failed: {str(e)}', 500)