"""
User Management Routes
CRUD operations for users, profile management
"""
from flask import Blueprint, request, session
from flask_bcrypt import generate_password_hash
from models import db, User, UserRole, Batch, user_batches, exam_batches
from utils.auth import login_required, require_role, get_current_user, check_user_access
from utils.response import success_response, error_response, paginated_response, serialize_user
from sqlalchemy import or_
import re
from datetime import datetime

users_bp = Blueprint('users', __name__)

def validate_phone(phone):
    """Validate phone number format"""
    phone = re.sub(r'[^\d]', '', phone)
    
    if phone.startswith('880'):
        phone = phone[3:]
    elif phone.startswith('+880'):
        phone = phone[4:]
    
    if len(phone) == 11 and phone.startswith('01'):
        return phone
    
    return None

@users_bp.route('', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_users():
    """Get all users with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role = request.args.get('role')
        search = request.args.get('search', '').strip()
        batch_id = request.args.get('batch_id', type=int)
        
        query = User.query
        
        # Filter by role
        if role and role in [r.value for r in UserRole]:
            query = query.filter(User.role == UserRole(role))
        
        # Filter by batch
        if batch_id:
            query = query.join(user_batches).filter(user_batches.c.batch_id == batch_id)
        
        # Search filter
        if search:
            search_filter = or_(
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.phone.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Order by creation date
        query = query.order_by(User.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        users = [serialize_user(user) for user in pagination.items]
        
        return paginated_response(
            users, 
            page, 
            per_page, 
            pagination.total, 
            "Users retrieved successfully"
        )
        
    except Exception as e:
        return error_response(f'Failed to retrieve users: {str(e)}', 500)

@users_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get specific user details"""
    try:
        current_user = get_current_user()
        
        # Check access permissions
        if not check_user_access(current_user, user_id):
            return error_response('Access denied', 403)
        
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        user_data = serialize_user(user)
        
        return success_response('User details retrieved', {'user': user_data})
        
    except Exception as e:
        return error_response(f'Failed to get user: {str(e)}', 500)

@users_bp.route('', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Required fields
        required_fields = ['phone', 'first_name', 'last_name', 'role']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        # Validate phone number
        phone = validate_phone(data['phone'])
        if not phone:
            return error_response('Invalid phone number format', 400)
        
        # Check if user already exists
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            return error_response('User with this phone number already exists', 409)
        
        # Validate role
        try:
            user_role = UserRole(data['role'])
        except ValueError:
            return error_response('Invalid user role', 400)
        
        # Validate email if provided
        email = data.get('email')
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return error_response('User with this email already exists', 409)
        
        # Create new user
        user = User(
            phone=phone,
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            email=email.strip() if email else None,
            role=user_role,
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            address=data.get('address', '').strip() if data.get('address') else None,
            guardian_phone=data.get('guardian_phone', '').strip() if data.get('guardian_phone') else None,
            emergency_contact=data.get('emergency_contact', '').strip() if data.get('emergency_contact') else None,
            sms_count=data.get('sms_count', 0)
        )
        
        # Set password for teachers and super users
        if user_role in [UserRole.TEACHER, UserRole.SUPER_USER]:
            password = data.get('password')
            if not password:
                return error_response('Password is required for teachers and super users', 400)
            
            if len(password) < 6:
                return error_response('Password must be at least 6 characters long', 400)
            
            user.password_hash = generate_password_hash(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Assign to batches if provided
        batch_ids = data.get('batch_ids', [])
        if batch_ids and user_role == UserRole.STUDENT:
            batches = Batch.query.filter(Batch.id.in_(batch_ids)).all()
            user.batches.extend(batches)
            db.session.commit()
        
        user_data = serialize_user(user)
        
        return success_response('User created successfully', {'user': user_data}, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create user: {str(e)}', 500)

@users_bp.route('/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update user information"""
    try:
        current_user = get_current_user()
        
        # Check access permissions
        if not check_user_access(current_user, user_id):
            return error_response('Access denied', 403)
        
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Update allowed fields
        updatable_fields = ['first_name', 'last_name', 'email', 'date_of_birth', 
                           'address', 'guardian_phone', 'emergency_contact', 'profile_image']
        
        # Only teachers and super users can update role and sms_count
        if current_user.role in [UserRole.TEACHER, UserRole.SUPER_USER]:
            updatable_fields.extend(['role', 'sms_count', 'is_active'])
        
        for field in updatable_fields:
            if field in data:
                if field == 'email' and data[field]:
                    # Check if email is already taken by another user
                    existing_email = User.query.filter(
                        User.email == data[field], 
                        User.id != user_id
                    ).first()
                    if existing_email:
                        return error_response('Email is already taken', 409)
                
                if field == 'date_of_birth' and data[field]:
                    try:
                        setattr(user, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                    except ValueError:
                        return error_response('Invalid date format. Use YYYY-MM-DD', 400)
                elif field == 'role' and data[field]:
                    try:
                        setattr(user, field, UserRole(data[field]))
                    except ValueError:
                        return error_response('Invalid user role', 400)
                else:
                    setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        
        # Update batch assignments for students
        if 'batch_ids' in data and user.role == UserRole.STUDENT:
            batch_ids = data['batch_ids']
            batches = Batch.query.filter(Batch.id.in_(batch_ids)).all()
            user.batches.clear()
            user.batches.extend(batches)
        
        db.session.commit()
        
        user_data = serialize_user(user)
        
        return success_response('User updated successfully', {'user': user_data})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update user: {str(e)}', 500)

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
@require_role(UserRole.SUPER_USER)
def delete_user(user_id):
    """Delete a user (soft delete by deactivating)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        # Don't allow deleting super users
        if user.role == UserRole.SUPER_USER:
            return error_response('Cannot delete super user', 403)
        
        # Soft delete by deactivating
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return success_response('User deactivated successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete user: {str(e)}', 500)

@users_bp.route('/students', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_students():
    """Get all students"""
    try:
        batch_id = request.args.get('batch_id', type=int)
        search = request.args.get('search', '').strip()
        
        query = User.query.filter(User.role == UserRole.STUDENT)
        
        if batch_id:
            query = query.join(user_batches).filter(user_batches.c.batch_id == batch_id)
        
        if search:
            search_filter = or_(
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.phone.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        students = query.order_by(User.first_name, User.last_name).all()
        
        students_data = [serialize_user(student) for student in students]
        
        return success_response('Students retrieved successfully', {'students': students_data})
        
    except Exception as e:
        return error_response(f'Failed to retrieve students: {str(e)}', 500)

@users_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@login_required
@require_role(UserRole.SUPER_USER)
def reset_user_password(user_id):
    """Reset user password (super user only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        if user.role == UserRole.STUDENT:
            return error_response('Cannot reset student password', 400)
        
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password:
            return error_response('New password is required', 400)
        
        if len(new_password) < 6:
            return error_response('Password must be at least 6 characters long', 400)
        
        user.password_hash = generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return success_response('Password reset successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to reset password: {str(e)}', 500)

@users_bp.route('/teachers', methods=['GET'])
@login_required
@require_role(UserRole.SUPER_USER)
def get_all_teachers():
    """Get all teachers for super admin management"""
    try:
        teachers = User.query.filter_by(role=UserRole.TEACHER, is_active=True).order_by(User.first_name, User.last_name).all()
        
        teachers_data = []
        for teacher in teachers:
            teachers_data.append({
                'id': teacher.id,
                'name': f"{teacher.first_name} {teacher.last_name}",
                'firstName': teacher.first_name,
                'lastName': teacher.last_name,
                'phoneNumber': teacher.phone,  # Fixed: Use 'phone' field
                'email': teacher.email or '',
                'smsCount': teacher.sms_count or 0,
                'lastLogin': teacher.last_login.isoformat() if teacher.last_login else None,
                'createdAt': teacher.created_at.isoformat() if teacher.created_at else None,
                'isActive': teacher.is_active
            })
        
        return success_response('Teachers retrieved successfully', teachers_data)
        
    except Exception as e:
        return error_response(f'Failed to retrieve teachers: {str(e)}', 500)

# Student-specific dashboard endpoints
@users_bp.route('/dashboard-stats', methods=['GET'])
@login_required
def get_student_dashboard_stats():
    """Get dashboard statistics for student"""
    try:
        current_user = get_current_user()
        
        if current_user.role != UserRole.STUDENT:
            return error_response('Only students can access this endpoint', 403)
        
        from models import ExamSubmission, Attendance, MonthlyMark, MonthlyExam
        from sqlalchemy import func
        
        # Get exam statistics
        total_exams = ExamSubmission.query.filter_by(user_id=current_user.id).count()
        
        # Get average score from exam submissions
        avg_score = db.session.query(func.avg(ExamSubmission.score)).filter_by(user_id=current_user.id).scalar()
        avg_score = round(avg_score) if avg_score else 0
        
        # Get attendance rate
        total_attendance = Attendance.query.filter_by(user_id=current_user.id).count()
        present_attendance = Attendance.query.filter_by(user_id=current_user.id, status='PRESENT').count()
        attendance_rate = round((present_attendance / total_attendance) * 100) if total_attendance > 0 else 0
        
        # Fee status (placeholder - you can implement based on your fee system)
        fee_status = "Paid"  # This would come from your fee management system
        
        stats = {
            'totalExams': total_exams,
            'averageScore': avg_score,
            'attendanceRate': attendance_rate,
            'feeStatus': fee_status
        }
        
        return success_response('Dashboard stats retrieved successfully', stats)
        
    except Exception as e:
        return error_response(f'Failed to retrieve dashboard stats: {str(e)}', 500)

@users_bp.route('/student/batch', methods=['GET'])
@login_required
def get_student_batch():
    """Get current student's batch information"""
    try:
        current_user = get_current_user()
        
        if current_user.role != UserRole.STUDENT:
            return error_response('Only students can access this endpoint', 403)
        
        if current_user.batches:
            batch = current_user.batches[0]  # Get first active batch
            batch_data = {
                'id': batch.id,
                'name': batch.name,
                'subject': batch.description,
                'is_active': batch.is_active
            }
            return success_response('Batch information retrieved successfully', batch_data)
        else:
            return success_response('No batch assigned', None)
        
    except Exception as e:
        return error_response(f'Failed to retrieve batch information: {str(e)}', 500)

@users_bp.route('/student/exam-results', methods=['GET'])
@login_required
def get_student_exam_results():
    """Get all exam results for current student"""
    try:
        current_user = get_current_user()
        
        if current_user.role != UserRole.STUDENT:
            return error_response('Only students can access this endpoint', 403)
        
        from models import ExamSubmission, Exam
        
        # Get exam submissions
        submissions = (ExamSubmission.query
                     .join(Exam)
                     .filter(ExamSubmission.user_id == current_user.id)
                     .order_by(ExamSubmission.submitted_at.desc())
                     .all())
        
        results = []
        for submission in submissions:
            exam = submission.exam
            percentage = round((submission.score / exam.total_marks) * 100) if exam.total_marks > 0 else 0
            
            # Calculate grade based on percentage
            if percentage >= 80:
                grade = 'A+'
            elif percentage >= 70:
                grade = 'A'
            elif percentage >= 60:
                grade = 'B'
            elif percentage >= 50:
                grade = 'C'
            elif percentage >= 40:
                grade = 'D'
            else:
                grade = 'F'
            
            results.append({
                'id': submission.id,
                'examId': exam.id,
                'examTitle': exam.title,
                'examSubject': exam.subject,
                'examType': exam.exam_type.value,
                'score': submission.score,
                'totalMarks': exam.total_marks,
                'percentage': percentage,
                'grade': grade,
                'submittedAt': submission.submitted_at.isoformat(),
                'feedback': submission.feedback,
                'marks': submission.score,  # Alias for compatibility
                'manualMarks': submission.manual_marks
            })
        
        return success_response('Exam results retrieved successfully', results)
        
    except Exception as e:
        return error_response(f'Failed to retrieve exam results: {str(e)}', 500)

@users_bp.route('/student/upcoming-exams', methods=['GET'])
@login_required
def get_student_upcoming_exams():
    """Get upcoming exams for current student"""
    try:
        current_user = get_current_user()
        
        if current_user.role != UserRole.STUDENT:
            return error_response('Only students can access this endpoint', 403)
        
        from models import Exam, ExamStatus
        from datetime import datetime
        
        # Get student's batches
        user_batch_ids = [b.id for b in current_user.batches if b.is_active]
        if not user_batch_ids:
            return success_response('No upcoming exams', [])
        
        now = datetime.utcnow()
        
        # Get upcoming exams
        upcoming_exams = (Exam.query
                        .join(exam_batches)
                        .filter(
                            exam_batches.c.batch_id.in_(user_batch_ids),
                            Exam.status == ExamStatus.ACTIVE,
                            Exam.start_time > now
                        )
                        .order_by(Exam.start_time)
                        .all())
        
        exams_data = []
        for exam in upcoming_exams:
            exams_data.append({
                'id': exam.id,
                'title': exam.title,
                'subject': exam.subject,
                'description': exam.description,
                'start_time': exam.start_time.isoformat(),
                'end_time': exam.end_time.isoformat(),
                'duration': exam.duration,
                'total_marks': exam.total_marks,
                'questions_count': len(exam.questions),
                'exam_type': exam.exam_type.value
            })
        
        return success_response('Upcoming exams retrieved successfully', exams_data)
        
    except Exception as e:
        return error_response(f'Failed to retrieve upcoming exams: {str(e)}', 500)

@users_bp.route('/student/attendance', methods=['GET'])
@login_required
def get_student_attendance():
    """Get attendance records for current student"""
    try:
        current_user = get_current_user()
        
        if current_user.role != UserRole.STUDENT:
            return error_response('Only students can access this endpoint', 403)
        
        from models import Attendance
        
        attendance_records = (Attendance.query
                            .filter_by(user_id=current_user.id)
                            .order_by(Attendance.attendance_date.desc())
                            .limit(30)  # Last 30 records
                            .all())
        
        records = []
        for record in attendance_records:
            records.append({
                'id': record.id,
                'date': record.attendance_date.isoformat(),
                'status': record.status,
                'checkInTime': record.check_in_time.strftime('%H:%M') if record.check_in_time else None,
                'checkOutTime': record.check_out_time.strftime('%H:%M') if record.check_out_time else None,
                'remarks': record.remarks
            })
        
        return success_response('Attendance records retrieved successfully', records)
        
    except Exception as e:
        return error_response(f'Failed to retrieve attendance records: {str(e)}', 500)

@users_bp.route('/student/monthly-exams', methods=['GET'])
@login_required
def get_student_monthly_exams():
    """Get monthly exam results for current student"""
    try:
        current_user = get_current_user()
        
        if current_user.role != UserRole.STUDENT:
            return error_response('Only students can access this endpoint', 403)
        
        from models import MonthlyExam, MonthlyRanking, MonthlyMark, IndividualExam
        
        # Get student's batches
        user_batch_ids = [b.id for b in current_user.batches if b.is_active]
        if not user_batch_ids:
            return success_response('No monthly exams found', [])
        
        # Get monthly exams for student's batches
        monthly_exams = (MonthlyExam.query
                       .filter(MonthlyExam.batch_id.in_(user_batch_ids))
                       .order_by(MonthlyExam.exam_date.desc())
                       .all())
        
        exams_data = []
        for exam in monthly_exams:
            # Get student's ranking for this exam
            ranking = MonthlyRanking.query.filter_by(
                monthly_exam_id=exam.id,
                user_id=current_user.id
            ).first()
            
            exam_data = {
                'id': exam.id,
                'title': exam.title,
                'exam_date': exam.exam_date.isoformat(),
                'batch_id': exam.batch_id,
                'batch_name': exam.batch.name if exam.batch else 'Unknown',
                'status': exam.status.value if exam.status else 'DRAFT',
                'student_result': None
            }
            
            if ranking:
                # Get individual exam marks
                individual_marks = (db.session.query(MonthlyMark, IndividualExam)
                                  .join(IndividualExam)
                                  .filter(
                                      MonthlyMark.monthly_exam_id == exam.id,
                                      MonthlyMark.user_id == current_user.id
                                  ).all())
                
                individual_exam_marks = []
                for mark, individual_exam in individual_marks:
                    individual_exam_marks.append({
                        'exam_id': individual_exam.id,
                        'subject': individual_exam.subject,
                        'title': individual_exam.title,
                        'marks_obtained': mark.marks_obtained,
                        'total_marks': mark.total_marks,
                        'percentage': mark.percentage,
                        'grade': mark.grade
                    })
                
                exam_data['student_result'] = {
                    'position': ranking.position,
                    'total_exam_marks': ranking.total_exam_marks,
                    'attendance_marks': ranking.attendance_marks,
                    'bonus_marks': ranking.bonus_marks,
                    'final_total': ranking.final_total,
                    'percentage': ranking.percentage,
                    'grade': ranking.grade,
                    'gpa': ranking.gpa,
                    'individual_exam_marks': individual_exam_marks
                }
            
            exams_data.append(exam_data)
        
        return success_response('Monthly exams retrieved successfully', exams_data)
        
    except Exception as e:
        return error_response(f'Failed to retrieve monthly exams: {str(e)}', 500)