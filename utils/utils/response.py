"""
Response Utilities
Standardized response formats for API endpoints
"""
from flask import jsonify
from datetime import datetime, date
from decimal import Decimal
import json

def success_response(message="Success", data=None, status_code=200):
    """Create a standardized success response"""
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = serialize_data(data)
    
    return jsonify(response), status_code

def error_response(message="Error", status_code=400, error_code=None):
    """Create a standardized error response"""
    response = {
        'success': False,
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if error_code:
        response['error_code'] = error_code
    
    return jsonify(response), status_code

def paginated_response(data, page, per_page, total, message="Data retrieved successfully"):
    """Create a paginated response"""
    response = {
        'success': True,
        'message': message,
        'data': serialize_data(data),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_next': page * per_page < total,
            'has_prev': page > 1
        },
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(response), 200

def serialize_data(data):
    """Serialize data for JSON response"""
    if isinstance(data, (datetime, date)):
        return data.isoformat()
    elif isinstance(data, Decimal):
        return float(data)
    elif hasattr(data, '__dict__'):
        # SQLAlchemy model instance
        return serialize_model(data)
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    else:
        return data

def serialize_model(model, exclude_fields=None):
    """Serialize SQLAlchemy model to dictionary"""
    if exclude_fields is None:
        exclude_fields = ['password_hash']
    
    result = {}
    
    for column in model.__table__.columns:
        field_name = column.name
        
        if field_name in exclude_fields:
            continue
        
        value = getattr(model, field_name)
        
        if isinstance(value, (datetime, date)):
            result[field_name] = value.isoformat() if value else None
        elif isinstance(value, Decimal):
            result[field_name] = float(value) if value else None
        elif hasattr(value, 'value'):  # Enum
            result[field_name] = value.value if value else None
        else:
            result[field_name] = value
    
    return result

def serialize_user(user, include_sensitive=False):
    """Serialize user model with role-specific data"""
    user_data = serialize_model(user, exclude_fields=['password_hash'] if not include_sensitive else [])
    
    # Add computed fields
    user_data['full_name'] = user.full_name
    
    # Add role-specific data
    if user.role.value == 'student':
        user_data['batches'] = [serialize_batch(batch) for batch in user.batches if batch.is_active]
    
    return user_data

def serialize_batch(batch):
    """Serialize batch model"""
    batch_data = serialize_model(batch)
    
    # Extract class from description if it exists
    class_name = None
    if batch.description and ' - ' in batch.description:
        class_name = batch.description.split(' - ')[0]
    
    # Add computed fields
    batch_data['class'] = class_name
    batch_data['student_count'] = len([s for s in batch.students if s.is_active])
    batch_data['currentStudents'] = len([s for s in batch.students if s.is_active])
    batch_data['maxStudents'] = batch.max_students or 50
    batch_data['isActive'] = batch.is_active
    
    return batch_data

def serialize_exam(exam, include_questions=False, include_submissions=False):
    """Serialize exam model"""
    exam_data = serialize_model(exam)
    
    # Add computed fields
    exam_data['question_count'] = len(exam.questions)
    exam_data['submission_count'] = len(exam.submissions)
    
    if include_questions:
        exam_data['questions'] = [serialize_question(q) for q in exam.questions if q.is_active]
    
    if include_submissions:
        exam_data['submissions'] = [serialize_submission(s) for s in exam.submissions]
    
    # Add batch information
    exam_data['batches'] = [{'id': b.id, 'name': b.name} for b in exam.batches]
    
    return exam_data

def serialize_question(question, include_correct_answer=False):
    """Serialize question model"""
    question_data = serialize_model(question)
    
    if not include_correct_answer:
        question_data.pop('correct_answer', None)
    
    return question_data

def serialize_submission(submission, include_answers=False):
    """Serialize exam submission"""
    submission_data = serialize_model(submission)
    
    if include_answers:
        submission_data['answers'] = [serialize_data(answer) for answer in submission.answers]
    
    return submission_data

def serialize_fee(fee):
    """Serialize fee model"""
    fee_data = serialize_model(fee)
    
    # Add computed fields
    total_amount = fee.amount + fee.late_fee - fee.discount
    fee_data['total_amount'] = float(total_amount)
    fee_data['is_overdue'] = fee.due_date < date.today() and fee.status.value == 'pending'
    
    return fee_data

def validate_json_request(required_fields=None):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            
            if not request.is_json:
                return error_response('Request must be JSON', 400)
            
            data = request.get_json()
            
            if not data:
                return error_response('Request data is required', 400)
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator