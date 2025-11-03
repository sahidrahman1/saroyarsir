"""
SMS Service - Python Implementation
BulkSMSBD API integration with balance tracking and templates
"""
import os
import json
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from flask import current_app
from models import SmsLog, SmsTemplate, User, Settings, db

logger = logging.getLogger(__name__)

@dataclass
class SMSConfig:
    """SMS Configuration"""
    api_key: str
    sender_id: str
    api_url: str = "http://bulksmsbd.net/api/smsapi"
    balance_url: str = "http://bulksmsbd.net/api/getBalanceApi"

@dataclass
class SMSMessage:
    """SMS Message structure"""
    recipient: str
    message: str
    sender_id: Optional[str] = None

@dataclass
class SMSResult:
    """SMS sending result"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    cost: float = 0.0
    balance_remaining: float = 0.0

class SMSService:
    """SMS Service for sending messages via BulkSMSBD"""
    
    def __init__(self):
        self._config: Optional[SMSConfig] = None

    @property
    def config(self) -> SMSConfig:
        """Lazily load SMS configuration"""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> SMSConfig:
        """Load SMS configuration from environment or database"""
        # Try environment variables first
        api_key = os.environ.get('BULKSMSBD_API_KEY', '')
        sender_id = os.environ.get('BULKSMSBD_SENDER_ID', 'SmartGarden')
        
        # If not in env, try database settings
        if not api_key:
            try:
                # This should be called from within a request or app context
                with current_app.app_context():
                    sms_settings = Settings.query.filter_by(key='sms_config').first()
                    if sms_settings and sms_settings.value:
                        config_data = sms_settings.value
                        api_key = config_data.get('api_key', '')
                        sender_id = config_data.get('sender_id', 'SmartGarden')
            except Exception as e:
                # This can happen if the app context is not available, which is expected
                # during initial module load. The config will be loaded on first use.
                logger.info(f"Could not load SMS config from database at this time: {e}")
        
        return SMSConfig(
            api_key=api_key,
            sender_id=sender_id
        )
    
    def check_balance(self) -> Dict[str, Any]:
        """Check SMS balance using BulkSMSBD API"""
        if not self.config.api_key:
            return {
                'success': False,
                'error': 'SMS API key not configured',
                'balance': 0
            }
        
        try:
            # BulkSMSBD Balance API format: GET http://bulksmsbd.net/api/getBalanceApi?api_key=YOUR_API_KEY
            params = {
                'api_key': self.config.api_key
            }
            
            response = requests.get(
                self.config.balance_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                # Response format: {"balance":"994"}
                data = response.json()
                balance = int(data.get('balance', 0)) if data.get('balance') else 0
                return {
                    'success': True,
                    'balance': balance,
                    'currency': 'BDT'
                }
            else:
                return {
                    'success': False,
                    'error': f'API returned status {response.status_code}',
                    'balance': 0
                }
                
        except Exception as e:
            logger.error(f"Error checking SMS balance: {e}")
            return {
                'success': False,
                'error': str(e),
                'balance': 0
            }
    
    def send_sms(self, message: SMSMessage, user_id: Optional[int] = None) -> SMSResult:
        """Send single SMS using BulkSMSBD API"""
        if not self.config.api_key:
            return SMSResult(
                success=False,
                error='SMS API key not configured'
            )
        
        try:
            # Format phone number for Bangladesh
            formatted_phone = self.clean_phone_number(message.recipient)
            if not formatted_phone.startswith('88'):
                formatted_phone = '88' + formatted_phone
            
            # BulkSMSBD API format: GET with parameters
            params = {
                'api_key': self.config.api_key,
                'type': 'text',
                'number': formatted_phone,
                'senderid': message.sender_id or self.config.sender_id,
                'message': message.message
            }
            
            # Send request using GET method
            response = requests.get(
                self.config.api_url,
                params=params,
                timeout=30
            )
            
            # Parse response
            result = self._parse_response(response, message, user_id)
            
            # Log the SMS
            self._log_sms(message, result, user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            result = SMSResult(
                success=False,
                error=str(e)
            )
            self._log_sms(message, result, user_id)
            return result
    
    def send_bulk_sms(self, messages: List[SMSMessage], user_id: Optional[int] = None) -> List[SMSResult]:
        """Send multiple SMS messages"""
        results = []
        
        for message in messages:
            result = self.send_sms(message, user_id)
            results.append(result)
            
            # Small delay between messages to avoid rate limiting
            import time
            time.sleep(0.1)
        
        return results

def send_attendance_notification(phone_number, student_name, status, date, batch_name, teacher_name):
    """
    Send attendance notification SMS to parent/guardian
    
    Args:
        phone_number (str): Phone number to send SMS to
        student_name (str): Name of the student
        status (str): Attendance status (present/absent)
        date (str): Date of attendance
        batch_name (str): Name of the batch/class
        teacher_name (str): Name of the teacher
        
    Returns:
        dict: Result of SMS sending operation
    """
    try:
        # Create SMS service instance
        sms_service = SMSService()
        
        # Format the message
        status_text = "PRESENT" if status.lower() == 'present' else "ABSENT"
        message = f"Attendance Alert: {student_name} was {status_text} on {date} in {batch_name}. Teacher: {teacher_name}. Thank you."
        
        # Send SMS
        result = sms_service.send_sms(phone_number, message, message_type='attendance')
        
        return {
            'success': result.success,
            'message': 'SMS sent successfully' if result.success else f'SMS failed: {result.error}',
            'response': {
                'message_id': result.message_id,
                'cost': result.cost,
                'balance_remaining': result.balance_remaining,
                'error': result.error
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to send attendance SMS: {e}")
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}',
            'response': {'error': str(e)}
        }

def send_bulk_attendance_sms(attendance_data, batch_name, date, teacher_name):
    """
    Send attendance SMS to multiple parents
    
    Args:
        attendance_data (list): List of attendance records with student and phone info
        batch_name (str): Name of the batch/class
        date (str): Date of attendance
        teacher_name (str): Name of the teacher
        
    Returns:
        dict: Summary of SMS sending results
    """
    results = {
        'total': len(attendance_data),
        'sent': 0,
        'failed': 0,
        'details': []
    }
    
    for item in attendance_data:
        student_name = item.get('student_name')
        phone_number = item.get('phone_number')
        status = item.get('status')
        
        if not phone_number:
            results['failed'] += 1
            results['details'].append({
                'student': student_name,
                'phone': phone_number,
                'status': 'failed',
                'error': 'No phone number'
            })
            continue
        
        result = send_attendance_notification(
            phone_number=phone_number,
            student_name=student_name,
            status=status,
            date=date,
            batch_name=batch_name,
            teacher_name=teacher_name
        )
        
        if result['success']:
            results['sent'] += 1
        else:
            results['failed'] += 1
            
        results['details'].append({
            'student': student_name,
            'phone': phone_number,
            'status': 'sent' if result['success'] else 'failed',
            'message': result['message']
        })
    
    return results
    
    def send_template_sms(self, template_id: int, recipients: List[str], 
                         variables: Dict[str, Any], user_id: Optional[int] = None) -> List[SMSResult]:
        """Send SMS using template"""
        try:
            # Get template
            template = SmsTemplate.query.get(template_id)
            if not template or not template.is_active:
                return [SMSResult(
                    success=False,
                    error='Template not found or inactive'
                )]
            
            # Process template content
            message_content = self._process_template(template.content, variables)
            
            # Create messages
            messages = [
                SMSMessage(recipient=recipient, message=message_content)
                for recipient in recipients
            ]
            
            # Send messages
            return self.send_bulk_sms(messages, user_id)
            
        except Exception as e:
            logger.error(f"Error sending template SMS: {e}")
            return [SMSResult(success=False, error=str(e))]
    
    def _parse_response(self, response: requests.Response, message: SMSMessage, user_id: Optional[int]) -> SMSResult:
        """Parse BulkSMSBD API response"""
        try:
            if response.status_code == 200:
                try:
                    data = response.json()
                    response_code = data.get('response_code')
                    success_message = data.get('success_message', '')
                    error_message = data.get('error_message', '')
                    
                    # BulkSMSBD success codes: 200 or 202
                    if response_code in [200, 202]:
                        return SMSResult(
                            success=True,
                            message_id=success_message,
                            cost=1.0,  # Each SMS costs 1 credit
                            balance_remaining=0  # Will be updated from balance API
                        )
                    else:
                        return SMSResult(
                            success=False,
                            error=error_message or f"API Error Code: {response_code}"
                        )
                except ValueError:
                    return SMSResult(
                        success=False,
                        error='Invalid API response format'
                    )
            else:
                return SMSResult(
                    success=False,
                    error=f'HTTP {response.status_code}: {response.text}'
                )
                
        except Exception as e:
            logger.error(f"Error parsing SMS response: {e}")
            return SMSResult(
                success=False,
                error=f'Response parsing error: {str(e)}'
            )
    
    def _log_sms(self, message: SMSMessage, result: SMSResult, user_id: Optional[int]):
        """Log SMS to database"""
        try:
            # Determine user if phone number provided
            logged_user = None
            if not user_id and message.recipient:
                clean_phone = self.clean_phone_number(message.recipient)
                logged_user = User.query.filter_by(phoneNumber=clean_phone).first()
                if logged_user:
                    user_id = logged_user.id
            
            # Create log entry
            sms_log = SmsLog(
                user_id=user_id,
                phone_number=message.recipient,
                message=message.message,
                status='sent' if result.success else 'failed',
                api_response={
                    'message_id': result.message_id,
                    'error': result.error,
                    'cost': result.cost,
                    'balance': result.balance_remaining
                },
                cost=result.cost,
                sent_at=datetime.utcnow() if result.success else None
            )
            
            db.session.add(sms_log)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging SMS: {e}")
            # Don't raise exception here as SMS might have been sent successfully
    
    def _process_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """Process template with variables"""
        content = template_content
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    def clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number"""
        # Remove all non-digit characters
        clean = ''.join(filter(str.isdigit, phone))
        
        # Handle Bangladesh phone numbers
        if clean.startswith('88'):
            clean = clean[2:]  # Remove country code
        elif clean.startswith('0'):
            clean = clean[1:]  # Remove leading zero
        
        # Add country code for international format
        if len(clean) == 11 and clean.startswith('1'):
            return f"88{clean}"
        
        return clean
    
    def contains_unicode(self, text: str) -> bool:
        """Check if text contains Unicode characters (Bengali)"""
        try:
            text.encode('ascii')
            return False
        except UnicodeEncodeError:
            return True
    
    def calculate_sms_count(self, text: str) -> Dict[str, Any]:
        """
        Calculate SMS count considering:
        - Pure English: 160 chars per SMS
        - Mixed Bangla/English: 100 chars per SMS (Unicode)
        - Pure Bangla: 70 chars per SMS (each Bangla char = ~2.2 English chars)
        """
        if not text:
            return {'sms_count': 0, 'char_count': 0, 'type': 'empty'}
        
        char_count = len(text)
        is_unicode = self.contains_unicode(text)
        
        # Check if text has Bangla characters
        has_bangla = any('\u0980' <= char <= '\u09FF' for char in text)
        
        if not is_unicode:
            # Pure English: 160 chars per SMS
            sms_count = 1 if char_count <= 160 else (char_count // 153) + (1 if char_count % 153 else 0)
            return {
                'sms_count': sms_count,
                'char_count': char_count,
                'type': 'english',
                'limit_per_sms': 160 if sms_count == 1 else 153,
                'chars_used': char_count,
                'chars_remaining': (160 if sms_count == 1 else 153 * sms_count) - char_count
            }
        
        if has_bangla:
            # Mixed or Pure Bangla: 100 chars per SMS (safer for mixed content)
            # Count Bangla chars with 2.2x weight
            bangla_count = sum(1 for char in text if '\u0980' <= char <= '\u09FF')
            english_count = char_count - bangla_count
            weighted_count = int(bangla_count * 2.2 + english_count)
            
            # Use 100 char limit for mixed content
            sms_count = 1 if weighted_count <= 100 else (weighted_count // 100) + (1 if weighted_count % 100 else 0)
            
            return {
                'sms_count': sms_count,
                'char_count': char_count,
                'weighted_count': weighted_count,
                'bangla_chars': bangla_count,
                'english_chars': english_count,
                'type': 'mixed' if english_count > 0 else 'bangla',
                'limit_per_sms': 100,
                'chars_used': weighted_count,
                'chars_remaining': (100 * sms_count) - weighted_count
            }
        
        # Unicode but not Bangla (other Unicode chars)
        sms_count = 1 if char_count <= 70 else (char_count // 67) + (1 if char_count % 67 else 0)
        return {
            'sms_count': sms_count,
            'char_count': char_count,
            'type': 'unicode',
            'limit_per_sms': 70 if sms_count == 1 else 67,
            'chars_used': char_count,
            'chars_remaining': (70 if sms_count == 1 else 67 * sms_count) - char_count
        }
    
    def truncate_message(self, text: str, max_sms: int = 1) -> str:
        """
        Truncate message to fit within max_sms count
        """
        if not text:
            return text
        
        is_unicode = self.contains_unicode(text)
        has_bangla = any('\u0980' <= char <= '\u09FF' for char in text)
        
        if has_bangla or is_unicode:
            # Mixed/Bangla: 100 chars per SMS
            max_chars = max_sms * 100
            
            # Calculate weighted length
            truncated = text
            while len(truncated) > 0:
                stats = self.calculate_sms_count(truncated)
                if stats['sms_count'] <= max_sms:
                    return truncated
                # Remove last 10 chars and try again
                truncated = truncated[:-10].strip()
            
            return text[:max_chars]
        else:
            # English: 160 chars for first SMS, 153 for subsequent
            max_chars = 160 if max_sms == 1 else (153 * max_sms)
            return text[:max_chars]
    
    def get_templates(self, category: Optional[str] = None) -> List[SmsTemplate]:
        """Get SMS templates"""
        query = SmsTemplate.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        return query.order_by(SmsTemplate.name).all()
    
    def create_template(self, name: str, subject: str, content: str, 
                       category: str, variables: List[str], user_id: int) -> SmsTemplate:
        """Create new SMS template"""
        template = SmsTemplate(
            name=name,
            subject=subject,
            content=content,
            category=category,
            variables=variables,
            created_by=user_id
        )
        
        db.session.add(template)
        db.session.commit()
        
        return template
    
    def update_template(self, template_id: int, **kwargs) -> Optional[SmsTemplate]:
        """Update SMS template"""
        template = SmsTemplate.query.get(template_id)
        if not template:
            return None
        
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        return template
    
    def delete_template(self, template_id: int) -> bool:
        """Delete SMS template"""
        template = SmsTemplate.query.get(template_id)
        if not template:
            return False
        
        template.is_active = False
        db.session.commit()
        
        return True

class SMSTemplateManager:
    """Manager for SMS templates with predefined templates"""
    
    def __init__(self):
        self.sms_service = SMSService()
    
    def get_default_templates(self) -> List[Dict[str, Any]]:
        """Get default SMS templates"""
        return [
            {
                'name': 'পরীক্ষার নোটিশ',
                'subject': 'Exam Notice',
                'content': 'প্রিয় {student_name}, আগামী {exam_date} তারিখে {exam_title} পরীক্ষা অনুষ্ঠিত হবে। সময়: {exam_time}। ধন্যবাদ।',
                'category': 'exam',
                'variables': ['student_name', 'exam_date', 'exam_title', 'exam_time']
            },
            {
                'name': 'ফি পেমেন্ট রিমাইন্ডার',
                'subject': 'Fee Payment Reminder',
                'content': 'প্রিয় {student_name}, আপনার {month} মাসের ফি {amount} টাকা বকেয়া আছে। শেষ তারিখ: {due_date}। যোগাযোগ: {contact}',
                'category': 'fee',
                'variables': ['student_name', 'month', 'amount', 'due_date', 'contact']
            },
            {
                'name': 'উপস্থিতি সতর্কতা',
                'subject': 'Attendance Warning',
                'content': 'প্রিয় {guardian_name}, {student_name} গত {days} দিন ক্লাসে অনুপস্থিত। উপস্থিতি: {attendance_rate}%। যোগাযোগ করুন।',
                'category': 'attendance',
                'variables': ['guardian_name', 'student_name', 'days', 'attendance_rate']
            },
            {
                'name': 'রেজাল্ট প্রকাশ',
                'subject': 'Result Published',
                'content': 'প্রিয় {student_name}, {exam_title} এর ফলাফল প্রকাশিত হয়েছে। প্রাপ্ত নম্বর: {marks}/{total_marks}। শতকরা: {percentage}%।',
                'category': 'result',
                'variables': ['student_name', 'exam_title', 'marks', 'total_marks', 'percentage']
            },
            {
                'name': 'সাধারণ নোটিশ',
                'subject': 'General Notice',
                'content': 'প্রিয় {recipient_name}, {notice_content} বিস্তারিত জানতে যোগাযোগ করুন: {contact}',
                'category': 'general',
                'variables': ['recipient_name', 'notice_content', 'contact']
            }
        ]
    
    def create_default_templates(self, user_id: int):
        """Create default templates if they don't exist"""
        existing_templates = {t.name for t in self.sms_service.get_templates()}
        
        for template_data in self.get_default_templates():
            if template_data['name'] not in existing_templates:
                self.sms_service.create_template(
                    name=template_data['name'],
                    subject=template_data['subject'],
                    content=template_data['content'],
                    category=template_data['category'],
                    variables=template_data['variables'],
                    user_id=user_id
                )

# Global instances
sms_service = SMSService()
template_manager = SMSTemplateManager()

# Helper functions for Flask integration
def send_notification_sms(user: User, message: str, category: str = 'general') -> SMSResult:
    """Send notification SMS to user"""
    if not user.phoneNumber:
        return SMSResult(success=False, error='User has no phone number')
    
    sms_message = SMSMessage(
        recipient=user.phoneNumber,
        message=message
    )
    
    return sms_service.send_sms(sms_message, user.id)

def send_bulk_notification(users: List[User], message: str, category: str = 'general') -> List[SMSResult]:
    """Send bulk notifications to multiple users"""
    messages = []
    
    for user in users:
        if user.phoneNumber:
            messages.append(SMSMessage(
                recipient=user.phoneNumber,
                message=message
            ))
    
    return sms_service.send_bulk_sms(messages)

def send_exam_notification(exam, students: List[User]) -> List[SMSResult]:
    """Send exam notification to students"""
    template = SmsTemplate.query.filter_by(
        category='exam',
        is_active=True
    ).first()
    
    if not template:
        # Fallback message
        message = f"পরীক্ষার নোটিশ: {exam.title} - {exam.start_time.strftime('%d/%m/%Y %I:%M %p')}"
        return send_bulk_notification(students, message, 'exam')
    
    results = []
    for student in students:
        if student.phoneNumber:
            variables = {
                'student_name': student.full_name,
                'exam_title': exam.title,
                'exam_date': exam.start_time.strftime('%d/%m/%Y'),
                'exam_time': exam.start_time.strftime('%I:%M %p')
            }
            
            result = sms_service.send_template_sms(
                template.id,
                [student.phoneNumber],
                variables,
                student.id
            )
            results.extend(result)
    
    return results