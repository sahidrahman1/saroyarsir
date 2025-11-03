"""
Settings API Routes
Application settings and configuration
"""
from flask import Blueprint, request, session
from models import db, User, UserRole
from utils.auth import login_required, require_role
from utils.response import success_response, error_response

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('', methods=['GET'])
@login_required
def get_settings():
    """Get application settings"""
    try:
        user_id = session.get('user_id')
        current_user = User.query.get(user_id)
        
        # Basic settings that can be displayed
        settings = {
            'app_name': 'SmartGardenHub',
            'version': '1.0.0',
            'user_role': current_user.role.value,
            'features': {
                'student_management': True,
                'batch_management': True,
                'exam_management': True,
                'attendance_tracking': True,
                'fee_management': True,
                'sms_integration': True,
                'question_builder': True,
                'online_exams': True
            },
            'ui_settings': {
                'theme': 'default',
                'sidebar_collapsed': False,
                'notifications_enabled': True
            }
        }
        
        return success_response('Settings retrieved successfully', settings)
        
    except Exception as e:
        return error_response(f'Failed to get settings: {str(e)}', 500)

@settings_bp.route('', methods=['PUT'])
@login_required
@require_role('super_user', 'teacher')
def update_settings():
    """Update application settings"""
    try:
        data = request.get_json()
        
        # For now, just return success
        # In a full implementation, you would save these to a settings table
        
        return success_response('Settings updated successfully', data)
        
    except Exception as e:
        return error_response(f'Failed to update settings: {str(e)}', 500)

@settings_bp.route('/profile', methods=['GET'])
@login_required
def get_profile_settings():
    """Get user profile settings"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        profile = {
            'id': user.id,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'email': user.email,
            'phoneNumber': user.phoneNumber,
            'role': user.role.value,
            'profileImage': user.profile_image,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        return success_response('Profile settings retrieved successfully', profile)
        
    except Exception as e:
        return error_response(f'Failed to get profile settings: {str(e)}', 500)

@settings_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile_settings():
    """Update user profile settings"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        data = request.get_json()
        
        # Update allowed fields
        if 'firstName' in data:
            user.first_name = data['firstName']
        if 'lastName' in data:
            user.last_name = data['lastName']
        if 'email' in data:
            user.email = data['email']
        if 'profileImage' in data:
            user.profile_image = data['profileImage']
        
        db.session.commit()
        
        return success_response('Profile updated successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update profile: {str(e)}', 500)