"""
SMS Management Routes
SMS sending, template management, and notification system
"""
from flask import Blueprint, request, jsonify
from models import db, SmsLog, User, Batch, UserRole, SmsStatus, user_batches
from utils.auth import login_required, require_role, get_current_user
from utils.response import success_response, error_response, paginated_response
from sqlalchemy import or_, func, extract
from datetime import datetime, date, timedelta
import requests
import os
import re

sms_bp = Blueprint('sms', __name__)

def count_sms_characters(text):
    """
    Count SMS characters where Bengali characters count as 2 and English as 1
    Bengali Unicode ranges: 0x0980-0x09FF
    """
    count = 0
    for char in text:
        # Check if character is Bengali (Unicode range 0x0980-0x09FF)
        if '\u0980' <= char <= '\u09FF':
            count += 2  # Bengali character counts as 2
        else:
            count += 1  # English and other characters count as 1
    return count

def validate_phone_number(phone):
    """Validate and format phone number"""
    # Remove any non-digit characters
    phone = re.sub(r'[^\d]', '', phone)
    
    # Handle country code
    if phone.startswith('880'):
        phone = phone[3:]
    elif phone.startswith('+880'):
        phone = phone[4:]
    
    # Validate Bangladesh mobile number format
    if len(phone) == 11 and phone.startswith('01'):
        return phone
    
    return None

def send_sms_via_api(phone, message):
    """Send SMS using BulkSMSBD API"""
    try:
        api_key = os.environ.get('SMS_API_KEY', 'gsOKLO6XtKsANCvgPHNt')
        sender_id = os.environ.get('SMS_SENDER_ID', '8809617628909')
        api_url = os.environ.get('SMS_API_URL', 'http://bulksmsbd.net/api/smsapi')
        
        # Format phone number - remove any spaces or special characters
        formatted_phone = phone.strip().replace(' ', '').replace('-', '').replace('+', '')
        
        # Ensure phone starts with 88 for Bangladesh
        if formatted_phone.startswith('0'):
            formatted_phone = '88' + formatted_phone
        elif not formatted_phone.startswith('88'):
            formatted_phone = '88' + formatted_phone
        
        # Build URL with GET parameters
        params = {
            'api_key': api_key,
            'type': 'text',
            'number': formatted_phone,
            'senderid': sender_id,
            'message': message
        }
        
        print(f"📤 Sending SMS to {formatted_phone}...")
        print(f"🔗 URL: {api_url}")
        print(f"📋 Params: {params}")
        
        # Send SMS using GET request
        response = requests.get(api_url, params=params, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                # Parse JSON response
                response_data = response.json()
                response_code = response_data.get('response_code')
                success_message = response_data.get('success_message', '')
                error_message = response_data.get('error_message', '')
                
                print(f"📊 Response Code: {response_code}")
                
                # BulkSMSBD success codes (typically 200 or 202)
                if response_code in [200, 202]:
                    print(f"✅ SMS sent successfully to {formatted_phone}")
                    return {
                        'success': True,
                        'message_id': success_message,
                        'cost': 1
                    }
                else:
                    print(f"❌ SMS API error (code {response_code}): {error_message}")
                    return {
                        'success': False,
                        'error': error_message or f"API Error Code: {response_code}"
                    }
            except ValueError:
                # Not JSON response - treat as error
                print(f"❌ Invalid JSON response: {response.text}")
                return {
                    'success': False,
                    'error': 'Invalid API response format'
                }
        else:
            error_msg = f'HTTP {response.status_code}: {response.text}'
            print(f"❌ SMS API HTTP error: {error_msg}")
            return {'success': False, 'error': error_msg}
    
    except requests.exceptions.Timeout:
        print(f"❌ SMS API timeout for {phone}")
        return {'success': False, 'error': 'SMS API timeout'}
    except Exception as e:
        print(f"❌ SMS API exception: {str(e)}")
        return {'success': False, 'error': str(e)}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'SMS API connection error'}
    except Exception as e:
        return {'success': False, 'error': f'SMS API error: {str(e)}'}

@sms_bp.route('/send', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def send_sms():
    """Send SMS to individual or multiple recipients"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        message = data.get('message', '').strip()
        recipients = data.get('recipients', [])  # List of phone numbers
        user_ids = data.get('user_ids', [])  # List of user IDs
        
        if not message:
            return error_response('Message is required', 400)
        
        # Validate character count (Bengali = 2, English = 1, max = 130)
        char_count = count_sms_characters(message)
        if char_count > 130:
            return error_response(f'Message exceeds character limit. Current: {char_count}/130 characters', 400)
        
        # Collect phone numbers
        phone_numbers = []
        
        # Add direct phone numbers
        for phone in recipients:
            formatted_phone = validate_phone_number(phone)
            if formatted_phone:
                phone_numbers.append(formatted_phone)
        
        # Add phone numbers from user IDs
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids), User.is_active == True).all()
            for user in users:
                formatted_phone = validate_phone_number(user.phone)
                if formatted_phone:
                    phone_numbers.append(formatted_phone)
        
        # Remove duplicates
        phone_numbers = list(set(phone_numbers))
        
        if not phone_numbers:
            return error_response('No valid phone numbers found', 400)
        
        # Check SMS quota for current user
        if current_user.sms_count < len(phone_numbers):
            return error_response(f'Insufficient SMS balance. Required: {len(phone_numbers)}, Available: {current_user.sms_count}', 400)
        
        # Send SMS to each recipient
        sent_count = 0
        failed_count = 0
        sms_logs = []
        
        for phone in phone_numbers:
            # Create SMS log entry
            sms_log = SmsLog(
                phone_number=phone,
                message=message,
                sent_by=current_user.id,
                status=SmsStatus.PENDING
            )
            
            # Find user by phone number
            user = User.query.filter_by(phone=phone).first()
            if user:
                sms_log.user_id = user.id
            
            # Send SMS
            result = send_sms_via_api(phone, message)
            
            if result['success']:
                sms_log.status = SmsStatus.SENT
                sms_log.sent_at = datetime.utcnow()
                sms_log.api_response = result
                sms_log.cost = result.get('cost', 1)
                sent_count += 1
            else:
                sms_log.status = SmsStatus.FAILED
                sms_log.api_response = result
                failed_count += 1
            
            db.session.add(sms_log)
            sms_logs.append(sms_log)
        
        # Update user's SMS count
        current_user.sms_count -= sent_count
        
        db.session.commit()
        
        result_data = {
            'total_recipients': len(phone_numbers),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'remaining_sms_balance': current_user.sms_count
        }
        
        return success_response(f'SMS sent to {sent_count} recipients', result_data)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to send SMS: {str(e)}', 500)

@sms_bp.route('/send-batch', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def send_batch_sms():
    """Send SMS to all students in specific batches"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        message = data.get('message', '').strip()
        batch_ids = data.get('batch_ids', [])
        include_guardians = data.get('include_guardians', False)
        
        if not message:
            return error_response('Message is required', 400)
        
        # Validate character count (Bengali = 2, English = 1, max = 130)
        char_count = count_sms_characters(message)
        if char_count > 130:
            return error_response(f'Message exceeds character limit. Current: {char_count}/130 characters', 400)
        
        if not batch_ids:
            return error_response('At least one batch must be selected', 400)
        
        # Validate batches
        batches = Batch.query.filter(Batch.id.in_(batch_ids), Batch.is_active == True).all()
        if len(batches) != len(batch_ids):
            return error_response('Some batch IDs are invalid', 400)
        
        # Get all students from selected batches
        students = User.query.filter(
            User.role == UserRole.STUDENT,
            User.is_active == True
        ).join(user_batches).filter(user_batches.c.batch_id.in_(batch_ids)).distinct().all()
        
        # Collect phone numbers
        phone_numbers = []
        
        for student in students:
            # Add student's phone number
            formatted_phone = validate_phone_number(student.phone)
            if formatted_phone:
                phone_numbers.append(formatted_phone)
            
            # Add guardian's phone number if requested
            if include_guardians and student.guardian_phone:
                guardian_phone = validate_phone_number(student.guardian_phone)
                if guardian_phone:
                    phone_numbers.append(guardian_phone)
        
        # Remove duplicates
        phone_numbers = list(set(phone_numbers))
        
        if not phone_numbers:
            return error_response('No valid phone numbers found in selected batches', 400)
        
        # Check SMS quota
        if current_user.sms_count < len(phone_numbers):
            return error_response(f'Insufficient SMS balance. Required: {len(phone_numbers)}, Available: {current_user.sms_count}', 400)
        
        # Send SMS to each recipient
        sent_count = 0
        failed_count = 0
        
        for phone in phone_numbers:
            # Create SMS log entry
            sms_log = SmsLog(
                phone_number=phone,
                message=message,
                sent_by=current_user.id,
                status=SmsStatus.PENDING
            )
            
            # Find user by phone number
            user = User.query.filter_by(phone=phone).first()
            if user:
                sms_log.user_id = user.id
            
            # Send SMS
            result = send_sms_via_api(phone, message)
            
            if result['success']:
                sms_log.status = SmsStatus.SENT
                sms_log.sent_at = datetime.utcnow()
                sms_log.api_response = result
                sms_log.cost = result.get('cost', 1)
                sent_count += 1
            else:
                sms_log.status = SmsStatus.FAILED
                sms_log.api_response = result
                failed_count += 1
            
            db.session.add(sms_log)
        
        # Update user's SMS count
        current_user.sms_count -= sent_count
        
        db.session.commit()
        
        result_data = {
            'total_recipients': len(phone_numbers),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'batches': [{'id': b.id, 'name': b.name} for b in batches],
            'remaining_sms_balance': current_user.sms_count
        }
        
        return success_response(f'Batch SMS sent to {sent_count} recipients', result_data)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to send batch SMS: {str(e)}', 500)

@sms_bp.route('/logs', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_sms_logs():
    """Get SMS logs with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        status = request.args.get('status')
        phone = request.args.get('phone', '').strip()
        sent_by = request.args.get('sent_by', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = SmsLog.query
        
        # Filter by status
        if status and status in [s.value for s in SmsStatus]:
            query = query.filter(SmsLog.status == SmsStatus(status))
        
        # Filter by phone number
        if phone:
            query = query.filter(SmsLog.phone_number.ilike(f'%{phone}%'))
        
        # Filter by sender
        if sent_by:
            query = query.filter(SmsLog.sent_by == sent_by)
        
        # Filter by date range
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(func.date(SmsLog.created_at) >= from_date)
            except ValueError:
                return error_response('Invalid date_from format. Use YYYY-MM-DD', 400)
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(func.date(SmsLog.created_at) <= to_date)
            except ValueError:
                return error_response('Invalid date_to format. Use YYYY-MM-DD', 400)
        
        # Join with sender user info
        query = query.join(User, SmsLog.sent_by == User.id, isouter=True)
        
        # Order by creation time
        query = query.order_by(SmsLog.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        logs = []
        for log in pagination.items:
            log_data = {
                'id': log.id,
                'phone_number': log.phone_number,
                'message': log.message,
                'status': log.status.value,
                'cost': float(log.cost) if log.cost else 0,
                'sent_at': log.sent_at.isoformat() if log.sent_at else None,
                'created_at': log.created_at.isoformat(),
                'sent_by_user': {
                    'id': log.sent_by_user.id,
                    'full_name': log.sent_by_user.full_name
                } if log.sent_by_user else None
            }
            
            # Add recipient user info if available
            if log.user:
                log_data['recipient_user'] = {
                    'id': log.user.id,
                    'full_name': log.user.full_name
                }
            
            logs.append(log_data)
        
        return paginated_response(
            logs, 
            page, 
            per_page, 
            pagination.total, 
            "SMS logs retrieved successfully"
        )
        
    except Exception as e:
        return error_response(f'Failed to retrieve SMS logs: {str(e)}', 500)

@sms_bp.route('/templates', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_sms_templates():
    """Get predefined SMS templates"""
    try:
        from flask import session
        custom_templates = session.get('custom_templates', {})
        
        templates = [
            {
                'id': 'attendance_present',
                'name': 'Attendance - Present',
                'category': 'attendance',
                'message': custom_templates.get('attendance_present', 'Dear Parent, {student_name} was PRESENT today in {batch_name} on {date}. Keep up the good work!'),
                'variables': ['student_name', 'batch_name', 'date'],
                'char_count': count_sms_characters(custom_templates.get('attendance_present', 'Dear Parent, {student_name} was PRESENT today in {batch_name} on {date}. Keep up the good work!')),
                'editable': True
            },
            {
                'id': 'attendance_absent',
                'name': 'Attendance - Absent',
                'category': 'attendance',
                'message': custom_templates.get('attendance_absent', 'Dear Parent, {student_name} was ABSENT today in {batch_name} on {date}. Please ensure regular attendance.'),
                'variables': ['student_name', 'batch_name', 'date'],
                'char_count': count_sms_characters(custom_templates.get('attendance_absent', 'Dear Parent, {student_name} was ABSENT today in {batch_name} on {date}. Please ensure regular attendance.')),
                'editable': True
            },
            {
                'id': 'exam_result',
                'name': 'Exam Result',
                'category': 'exam',
                'message': custom_templates.get('exam_result', 'Dear Parent, {student_name} scored {marks}/{total} marks in {subject} exam on {date}. Total marks: {marks}/{total}'),
                'variables': ['student_name', 'subject', 'marks', 'total', 'date'],
                'char_count': count_sms_characters(custom_templates.get('exam_result', 'Dear Parent, {student_name} scored {marks}/{total} marks in {subject} exam on {date}. Total marks: {marks}/{total}')),
                'editable': True
            }
        ]
        
        return jsonify(templates)
        
    except Exception as e:
        return error_response(f'Failed to get SMS templates: {str(e)}', 500)

@sms_bp.route('/templates/<template_id>', methods=['PUT'])
@login_required
def update_sms_template(template_id):
    """Update an SMS template"""
    try:
        data = request.get_json()
        new_message = data.get('message', '').strip()
        
        if not new_message:
            return error_response('Message is required', 400)
        
        # Validate message length
        char_count = count_sms_characters(new_message)
        if char_count > 130:
            return error_response(f'Message exceeds 130 character limit ({char_count} chars)', 400)
        
        # Get current templates
        templates = [
            {
                'id': 'attendance_present',
                'name': 'Attendance - Present',
                'category': 'attendance',
                'message': 'Dear Parent, {student_name} was PRESENT today in {batch_name} on {date}. Keep up the good work!',
                'variables': ['student_name', 'batch_name', 'date'],
                'char_count': 95,
                'editable': True
            },
            {
                'id': 'attendance_absent',
                'name': 'Attendance - Absent',
                'category': 'attendance',
                'message': 'Dear Parent, {student_name} was ABSENT today in {batch_name} on {date}. Please ensure regular attendance.',
                'variables': ['student_name', 'batch_name', 'date'],
                'char_count': 108,
                'editable': True
            },
            {
                'id': 'exam_good',
                'name': 'Exam - Good Performance',
                'category': 'exam',
                'message': 'Congratulations! {student_name} scored {marks}/{total} in {subject} exam on {date}. Excellent performance!',
                'variables': ['student_name', 'subject', 'marks', 'total', 'date'],
                'char_count': 102,
                'editable': True
            },
            {
                'id': 'exam_poor',
                'name': 'Exam - Needs Improvement',
                'category': 'exam',
                'message': '{student_name} scored {marks}/{total} in {subject} on {date}. Please encourage more practice.',
                'variables': ['student_name', 'subject', 'marks', 'total', 'date'],
                'char_count': 91,
                'editable': True
            }
        ]
        
        # Find and update the template
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return error_response('Template not found', 404)
        
        # Update template message in session/database (for now, we'll use session)
        from flask import session
        if 'custom_templates' not in session:
            session['custom_templates'] = {}
        
        session['custom_templates'][template_id] = new_message
        session.modified = True
        
        return success_response('Template updated successfully', {
            'template_id': template_id,
            'message': new_message,
            'char_count': char_count
        })
        
    except Exception as e:
        return error_response(f'Failed to update template: {str(e)}', 500)

@sms_bp.route('/validate-message', methods=['POST'])
@login_required
def validate_sms_message():
    """Validate SMS message character count"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return success_response('Message validated', {
                'char_count': 0,
                'max_characters': 130,
                'remaining': 130,
                'is_valid': True,
                'estimated_sms': 0
            })
        
        # Count characters (Bengali = 2, English = 1)
        char_count = count_sms_characters(message)
        remaining = 130 - char_count
        is_valid = char_count <= 130
        
        # Estimate number of SMS (1 SMS = 130 chars)
        estimated_sms = (char_count // 130) + (1 if char_count % 130 > 0 else 0)
        
        return success_response('Message validated', {
            'char_count': char_count,
            'max_characters': 130,
            'remaining': remaining,
            'is_valid': is_valid,
            'estimated_sms': estimated_sms,
            'message_length': len(message)
        })
        
    except Exception as e:
        return error_response(f'Failed to validate message: {str(e)}', 500)

@sms_bp.route('/balance', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_sms_balance():
    """Get current user's SMS balance"""
    try:
        current_user = get_current_user()
        
        # Get usage statistics
        total_sent = SmsLog.query.filter(
            SmsLog.sent_by == current_user.id,
            SmsLog.status == SmsStatus.SENT
        ).count()
        
        # Get monthly usage
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_sent = SmsLog.query.filter(
            SmsLog.sent_by == current_user.id,
            SmsLog.status == SmsStatus.SENT,
            extract('month', SmsLog.sent_at) == current_month,
            extract('year', SmsLog.sent_at) == current_year
        ).count()
        
        # Get recent activity
        recent_activity = SmsLog.query.filter(
            SmsLog.sent_by == current_user.id
        ).order_by(SmsLog.created_at.desc()).limit(5).all()
        
        recent_logs = []
        for log in recent_activity:
            recent_logs.append({
                'phone_number': log.phone_number,
                'message': log.message[:50] + '...' if len(log.message) > 50 else log.message,
                'status': log.status.value,
                'sent_at': log.sent_at.isoformat() if log.sent_at else log.created_at.isoformat()
            })
        
        balance_info = {
            'current_balance': current_user.sms_count,
            'total_sent': total_sent,
            'monthly_sent': monthly_sent,
            'recent_activity': recent_logs
        }
        
        return success_response('SMS balance retrieved', {'balance': balance_info})
        
    except Exception as e:
        return error_response(f'Failed to get SMS balance: {str(e)}', 500)

@sms_bp.route('/balance/add', methods=['POST'])
@login_required
@require_role(UserRole.SUPER_USER)
def add_sms_balance():
    """Add SMS balance to a user (Super user only)"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        user_id = data.get('user_id')
        amount = data.get('amount')
        
        if not user_id or not amount:
            return error_response('User ID and amount are required', 400)
        
        if not isinstance(amount, int) or amount <= 0:
            return error_response('Amount must be a positive integer', 400)
        
        # Validate user
        user = User.query.filter_by(id=user_id, is_active=True).first()
        if not user:
            return error_response('User not found', 404)
        
        if user.role == UserRole.STUDENT:
            return error_response('Cannot add SMS balance to students', 400)
        
        # Add balance
        user.sms_count += amount
        db.session.commit()
        
        result_data = {
            'user_id': user.id,
            'user_name': user.full_name,
            'added_amount': amount,
            'new_balance': user.sms_count
        }
        
        return success_response(f'{amount} SMS credits added successfully', result_data)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to add SMS balance: {str(e)}', 500)

@sms_bp.route('/statistics', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_sms_statistics():
    """Get SMS usage statistics"""
    try:
        # Get date range
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        
        # Basic statistics
        total_sent = SmsLog.query.filter(
            SmsLog.status == SmsStatus.SENT,
            SmsLog.sent_at >= start_date
        ).count()
        
        total_failed = SmsLog.query.filter(
            SmsLog.status == SmsStatus.FAILED,
            SmsLog.created_at >= start_date
        ).count()
        
        # Success rate
        total_attempts = total_sent + total_failed
        success_rate = (total_sent / total_attempts * 100) if total_attempts > 0 else 0
        
        # Daily statistics
        daily_stats = db.session.query(
            func.date(SmsLog.sent_at).label('date'),
            func.count(SmsLog.id).label('count')
        ).filter(
            SmsLog.status == SmsStatus.SENT,
            SmsLog.sent_at >= start_date
        ).group_by(func.date(SmsLog.sent_at)).order_by('date').all()
        
        daily_data = [{'date': stat.date.isoformat(), 'count': stat.count} for stat in daily_stats]
        
        # Top senders
        top_senders = db.session.query(
            User.full_name,
            func.count(SmsLog.id).label('count')
        ).join(SmsLog, User.id == SmsLog.sent_by).filter(
            SmsLog.status == SmsStatus.SENT,
            SmsLog.sent_at >= start_date
        ).group_by(User.id, User.full_name).order_by(func.count(SmsLog.id).desc()).limit(5).all()
        
        top_senders_data = [{'name': sender.full_name, 'count': sender.count} for sender in top_senders]
        
        statistics = {
            'period_days': days,
            'total_sent': total_sent,
            'total_failed': total_failed,
            'success_rate': round(success_rate, 2),
            'daily_stats': daily_data,
            'top_senders': top_senders_data
        }
        
        return success_response('SMS statistics retrieved', {'statistics': statistics})
        
    except Exception as e:
        return error_response(f'Failed to get SMS statistics: {str(e)}', 500)

@sms_bp.route('/add-credits', methods=['POST'])
@login_required
@require_role(UserRole.SUPER_USER)
def add_sms_credits():
    """Add SMS credits to a teacher (Super Admin only)"""
    try:
        data = request.get_json()
        teacher_id = data.get('teacher_id')
        credits = data.get('credits')
        memo = data.get('memo', 'Credits added by Super Admin')
        
        if not teacher_id or not credits:
            return error_response('Teacher ID and credits are required', 400)
        
        if not isinstance(credits, int) or credits <= 0:
            return error_response('Credits must be a positive integer', 400)
            
        if credits > 10000:
            return error_response('Cannot add more than 10,000 credits at once', 400)
        
        # Get teacher
        teacher = User.query.filter_by(id=teacher_id, role=UserRole.TEACHER, is_active=True).first()
        if not teacher:
            return error_response('Teacher not found', 404)
        
        # Add credits
        old_balance = teacher.sms_count or 0
        teacher.sms_count = old_balance + credits
        teacher.updated_at = datetime.utcnow()
        
        # Log the transaction
        current_user = get_current_user()
        
        # Create SMS log for audit (using correct field names)
        sms_log = SmsLog(
            user_id=teacher.id,
            phone_number=teacher.phone,
            message=f"SMS Credits Added: {credits} credits. New balance: {teacher.sms_count}. Memo: {memo}",
            status=SmsStatus.SENT,
            sent_by=current_user.id,
            api_response={'type': 'credit_addition', 'added_by': f"{current_user.first_name} {current_user.last_name}", 'memo': memo},
            cost=0,
            sent_at=datetime.utcnow()
        )
        
        db.session.add(sms_log)
        db.session.commit()
        
        return success_response(f'Successfully added {credits} SMS credits to {teacher.first_name} {teacher.last_name}', {
            'teacher_id': teacher.id,
            'teacher_name': f"{teacher.first_name} {teacher.last_name}",
            'credits_added': credits,
            'old_balance': old_balance,
            'new_balance': teacher.sms_count,
            'memo': memo
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to add SMS credits: {str(e)}', 500)

@sms_bp.route('/stats', methods=['GET'])
@login_required
@require_role(UserRole.SUPER_USER)
def get_sms_system_stats():
    """Get SMS system statistics (Super Admin only)"""
    try:
        # Get all teachers with their SMS counts
        teachers = User.query.filter_by(role=UserRole.TEACHER, is_active=True).all()
        
        total_credits_distributed = sum(teacher.sms_count or 0 for teacher in teachers)
        active_teachers = len([t for t in teachers if (t.sms_count or 0) > 0])
        
        # Get total SMS sent (approximation of credits used)
        total_sent = SmsLog.query.filter_by(status=SmsStatus.SENT).count()
        
        stats = {
            'totalCreditsDistributed': total_credits_distributed,
            'totalCreditsUsed': total_sent,  # Approximation
            'activeTeachers': active_teachers,
            'totalTeachers': len(teachers)
        }
        
        return success_response('SMS system statistics retrieved', stats)
        
    except Exception as e:
        return error_response(f'Failed to get SMS system statistics: {str(e)}', 500)