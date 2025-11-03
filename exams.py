"""
Exam Management Routes
Create, manage, and handle exam submissions including monthly exams
"""
from flask import Blueprint, request
from models import db, Exam, Question, ExamSubmission, ExamAnswer, Batch, User, UserRole, ExamType, ExamStatus, SubmissionStatus, QuestionType, exam_batches
from utils.auth import login_required, require_role, get_current_user
from utils.response import success_response, error_response, serialize_exam
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
import json

exams_bp = Blueprint('exams', __name__)

@exams_bp.route('', methods=['GET'])
@login_required
def get_exams():
    """Get exams with filtering"""
    try:
        current_user = get_current_user()
        batch_id = request.args.get('batch_id', type=int)
        status = request.args.get('status')
        exam_type = request.args.get('exam_type')
        search = request.args.get('search', '').strip()
        
        query = Exam.query
        
        # Filter based on user role
        if current_user.role == UserRole.STUDENT:
            # Students can only see exams for their batches
            user_batch_ids = [b.id for b in current_user.batches if b.is_active]
            if not user_batch_ids:
                return success_response('No exams found', [])
            query = query.join(exam_batches).filter(exam_batches.c.batch_id.in_(user_batch_ids))
        
        # Apply filters
        if batch_id:
            query = query.join(exam_batches).filter(exam_batches.c.batch_id == batch_id)
        
        if status:
            try:
                query = query.filter(Exam.status == ExamStatus(status))
            except ValueError:
                return error_response('Invalid status', 400)
        
        if exam_type:
            try:
                query = query.filter(Exam.exam_type == ExamType(exam_type))
            except ValueError:
                return error_response('Invalid exam type', 400)
        
        if search:
            query = query.filter(or_(
                Exam.title.ilike(f'%{search}%'),
                Exam.description.ilike(f'%{search}%')
            ))
        
        # Order by start time
        exams = query.order_by(Exam.start_time.desc()).all()
        
        exam_list = []
        for exam in exams:
            exam_data = serialize_exam(exam)
            
            # Add submission status for students
            if current_user.role == UserRole.STUDENT:
                submission = ExamSubmission.query.filter_by(
                    exam_id=exam.id,
                    user_id=current_user.id
                ).first()
                
                exam_data['submission_status'] = submission.status.value if submission else None
                exam_data['submitted_at'] = submission.submitted_at.isoformat() if submission and submission.submitted_at else None
                exam_data['can_take'] = (
                    exam.status == ExamStatus.ACTIVE and
                    datetime.utcnow() >= exam.start_time and
                    datetime.utcnow() <= exam.end_time and
                    not submission
                )
            
            exam_list.append(exam_data)
        
        return success_response('Exams retrieved successfully', exam_list)
        
    except Exception as e:
        return error_response(f'Failed to retrieve exams: {str(e)}', 500)

@exams_bp.route('', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def create_exam():
    """Create a new exam"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Required fields
        required_fields = ['title', 'duration', 'start_time', 'end_time', 'batch_ids']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        # Parse and validate dates
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            
            if end_time <= start_time:
                return error_response('End time must be after start time', 400)
            
        except ValueError:
            return error_response('Invalid datetime format', 400)
        
        # Validate exam type
        exam_type = ExamType.ONLINE
        if data.get('exam_type'):
            try:
                exam_type = ExamType(data['exam_type'])
            except ValueError:
                return error_response('Invalid exam type', 400)
        
        # Validate duration
        duration = data.get('duration', 60)
        if not isinstance(duration, int) or duration <= 0:
            return error_response('Duration must be a positive integer (minutes)', 400)
        
        # Create exam
        exam = Exam(
            title=data['title'],
            description=data.get('description', ''),
            exam_type=exam_type,
            duration=duration,
            total_marks=data.get('total_marks', 100),
            pass_marks=data.get('pass_marks', 40),
            start_time=start_time,
            end_time=end_time,
            instructions=data.get('instructions', ''),
            status=ExamStatus.DRAFT,
            is_monthly_exam=data.get('is_monthly_exam', False),
            created_by=get_current_user().id
        )
        
        db.session.add(exam)
        db.session.flush()  # Get the exam ID
        
        # Add batch associations
        batch_ids = data.get('batch_ids', [])
        if batch_ids:
            for batch_id in batch_ids:
                batch = Batch.query.get(batch_id)
                if batch:
                    exam.batches.append(batch)
        
        db.session.commit()
        
        return success_response('Exam created successfully', {'exam': serialize_exam(exam)}, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create exam: {str(e)}', 500)

@exams_bp.route('/monthly', methods=['GET'])
@login_required
def get_monthly_exams():
    """Get monthly exams with filtering"""
    try:
        current_user = get_current_user()
        batch_id = request.args.get('batch_id', type=int)
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        query = Exam.query.filter(Exam.is_monthly_exam == True)
        
        # Filter based on user role
        if current_user.role == UserRole.STUDENT:
            user_batch_ids = [b.id for b in current_user.batches if b.is_active]
            if not user_batch_ids:
                return success_response('No monthly exams found', [])
            query = query.join(exam_batches).filter(exam_batches.c.batch_id.in_(user_batch_ids))
        
        # Apply filters
        if batch_id:
            query = query.join(exam_batches).filter(exam_batches.c.batch_id == batch_id)
        
        if month and year:
            from sqlalchemy import extract
            query = query.filter(
                extract('month', Exam.start_time) == month,
                extract('year', Exam.start_time) == year
            )
        elif year:
            from sqlalchemy import extract
            query = query.filter(extract('year', Exam.start_time) == year)
        
        exams = query.order_by(Exam.start_time.desc()).all()
        
        exam_list = []
        for exam in exams:
            exam_data = serialize_exam(exam)
            
            if current_user.role == UserRole.STUDENT:
                submission = ExamSubmission.query.filter_by(
                    exam_id=exam.id,
                    user_id=current_user.id
                ).first()
                
                exam_data['submission_status'] = submission.status.value if submission else None
                exam_data['score'] = submission.score if submission else None
                exam_data['percentage'] = submission.percentage if submission else None
            
            exam_list.append(exam_data)
        
        return success_response('Monthly exams retrieved successfully', exam_list)
        
    except Exception as e:
        return error_response(f'Failed to retrieve monthly exams: {str(e)}', 500)
