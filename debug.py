"""
Debug routes to check data
"""
from flask import Blueprint, request
from models import db, User, UserRole, Batch
from utils.response import success_response

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/check-data', methods=['GET'])
def check_data():
    """Check if test data exists"""
    try:
        # Check batches
        batches = Batch.query.all()
        batch_data = []
        for batch in batches:
            students = [s for s in batch.students if s.is_active]
            batch_info = {
                'id': batch.id,
                'name': batch.name,
                'student_count': len(students),
                'students': [{'id': s.id, 'name': s.full_name, 'phone': s.phoneNumber} for s in students[:5]]  # First 5 students
            }
            batch_data.append(batch_info)
        
        # Check users
        students = User.query.filter_by(role=UserRole.STUDENT, is_active=True).all()
        teachers = User.query.filter_by(role=UserRole.TEACHER, is_active=True).all()
        
        return success_response('Data check completed', {
            'batches': batch_data,
            'total_students': len(students),
            'total_teachers': len(teachers),
            'student_sample': [{'id': s.id, 'name': s.full_name, 'phone': s.phoneNumber} for s in students[:3]]
        })
        
    except Exception as e:
        return {'error': str(e)}, 500

@debug_bp.route('/test-marks', methods=['POST'])
def test_marks():
    """Test marks submission without authentication"""
    try:
        data = request.get_json()
        return success_response('Test marks endpoint working', {
            'received_data': data,
            'data_type': type(data).__name__,
            'keys': list(data.keys()) if isinstance(data, dict) else 'Not a dict'
        })
    except Exception as e:
        return {'error': str(e)}, 500