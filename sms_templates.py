"""
SMS Template Management Routes
Manage SMS templates for various notifications
"""
from flask import Blueprint, request, jsonify, session
from models import db, Settings, User
from utils.auth import login_required, require_role, get_current_user
from utils.response import success_response, error_response
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

sms_templates_bp = Blueprint('sms_templates', __name__)

@sms_templates_bp.route('', methods=['GET'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def get_templates():
    """Get all SMS templates"""
    try:
        # Get templates from database
        db_templates = Settings.query.filter(
            Settings.key.like('sms_template_%')
        ).all()
        
        # Get session templates
        session_templates = session.get('custom_templates', {})
        
        templates = {
            'exam_result': {
                'name': 'Exam Result',
                'description': 'Template for exam result notifications',
                'variables': ['student_name', 'subject', 'marks', 'total', 'grade', 'date'],
                'default': "Dear Parent, {student_name} scored {marks}/{total} marks in {subject} exam on {date}. Grade: {grade}",
                'current': session_templates.get('exam_result', ''),
                'saved': None
            },
            'attendance': {
                'name': 'Attendance',
                'description': 'Template for attendance notifications',
                'variables': ['student_name', 'status', 'date'],
                'default': "Dear Parent, {student_name} was {status} in class on {date}.",
                'current': session_templates.get('attendance', ''),
                'saved': None
            },
            'fee_reminder': {
                'name': 'Fee Reminder',
                'description': 'Template for fee reminder notifications',
                'variables': ['student_name', 'amount', 'due_date'],
                'default': "Dear Parent, monthly fee for {student_name} is due. Amount: {amount} BDT. Please pay by {due_date}.",
                'current': session_templates.get('fee_reminder', ''),
                'saved': None
            }
        }
        
        # Update with saved templates from database
        for db_template in db_templates:
            template_type = db_template.key.replace('sms_template_', '')
            if template_type in templates:
                templates[template_type]['saved'] = db_template.value.get('message', '') if db_template.value else ''
        
        return success_response('Templates retrieved successfully', templates)
        
    except Exception as e:
        logger.error(f"Error getting SMS templates: {e}")
        return error_response('Failed to retrieve templates', 500)

@sms_templates_bp.route('/<template_type>', methods=['POST'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def update_template(template_type):
    """Update SMS template (session-based for live editing)"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return error_response('Template message is required', 400)
        
        message = data['message'].strip()
        if not message:
            return error_response('Template message cannot be empty', 400)
        
        # Store in session for immediate use
        if 'custom_templates' not in session:
            session['custom_templates'] = {}
        
        session['custom_templates'][template_type] = message
        session.permanent = True
        
        return success_response('Template updated successfully', {
            'template_type': template_type,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Error updating SMS template: {e}")
        return error_response('Failed to update template', 500)

@sms_templates_bp.route('/<template_type>/save', methods=['POST'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def save_template(template_type):
    """Save SMS template to database permanently"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return error_response('Template message is required', 400)
        
        message = data['message'].strip()
        if not message:
            return error_response('Template message cannot be empty', 400)
        
        current_user = get_current_user()
        template_key = f"sms_template_{template_type}"
        
        # Check if template exists
        template_setting = Settings.query.filter_by(key=template_key).first()
        
        if template_setting:
            # Update existing template
            template_setting.value = {'message': message}
            template_setting.updated_by = current_user.id
            template_setting.updated_at = datetime.utcnow()
        else:
            # Create new template
            template_setting = Settings(
                key=template_key,
                value={'message': message},
                description=f"SMS template for {template_type}",
                category="sms_templates",
                updated_by=current_user.id
            )
            db.session.add(template_setting)
        
        db.session.commit()
        
        return success_response('Template saved successfully', {
            'template_type': template_type,
            'message': message
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving SMS template: {e}")
        return error_response('Failed to save template', 500)

@sms_templates_bp.route('/<template_type>/reset', methods=['POST'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def reset_template(template_type):
    """Reset SMS template to default"""
    try:
        # Remove from session
        if 'custom_templates' in session and template_type in session['custom_templates']:
            del session['custom_templates'][template_type]
        
        # Get default template
        default_templates = {
            'exam_result': "Dear Parent, {student_name} scored {marks}/{total} marks in {subject} exam on {date}. Grade: {grade}",
            'attendance': "Dear Parent, {student_name} was {status} in class on {date}.",
            'fee_reminder': "Dear Parent, monthly fee for {student_name} is due. Amount: {amount} BDT. Please pay by {due_date}."
        }
        
        default_message = default_templates.get(template_type, "Default template not found")
        
        return success_response('Template reset to default', {
            'template_type': template_type,
            'message': default_message
        })
        
    except Exception as e:
        logger.error(f"Error resetting SMS template: {e}")
        return error_response('Failed to reset template', 500)

@sms_templates_bp.route('/preview', methods=['POST'])
@login_required
@require_role('TEACHER', 'SUPER_USER')
def preview_template():
    """Preview SMS template with sample data"""
    try:
        data = request.get_json()
        
        if not data or 'template' not in data or 'template_type' not in data:
            return error_response('Template and template type are required', 400)
        
        template = data['template']
        template_type = data['template_type']
        
        # Sample data for different template types
        sample_data = {
            'exam_result': {
                'student_name': 'আহমেদ আলী',
                'subject': 'গণিত',
                'marks': 85,
                'total': 100,
                'grade': 'A',
                'percentage': 85.0,
                'date': datetime.now().strftime('%d/%m/%Y')
            },
            'attendance': {
                'student_name': 'ফাতিমা খান',
                'status': 'উপস্থিত',
                'date': datetime.now().strftime('%d/%m/%Y')
            },
            'fee_reminder': {
                'student_name': 'রহিম উদ্দিন',
                'amount': 2500,
                'due_date': '৩১/১২/২০২৪'
            }
        }
        
        try:
            # Generate preview message
            preview_data = sample_data.get(template_type, {})
            preview_message = template.format(**preview_data)
            
            return success_response('Preview generated successfully', {
                'preview': preview_message,
                'length': len(preview_message),
                'sms_count': 1 if len(preview_message) <= 160 else 2,
                'sample_data': preview_data
            })
            
        except KeyError as e:
            return error_response(f'Invalid template variable: {str(e)}', 400)
        except Exception as e:
            return error_response(f'Template format error: {str(e)}', 400)
        
    except Exception as e:
        logger.error(f"Error previewing SMS template: {e}")
        return error_response('Failed to generate preview', 500)
