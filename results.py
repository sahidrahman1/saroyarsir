"""
Results Management Routes
Monthly result calculation and reporting
"""
from flask import Blueprint, request
from models import db, MonthlyResult, User, Batch, ExamSubmission, Attendance, Fee, UserRole, AttendanceStatus, FeeStatus
from utils.auth import login_required, require_role, get_current_user, check_batch_access
from utils.response import success_response, error_response, paginated_response
from sqlalchemy import or_, and_, func, extract, case
from datetime import datetime, date
import calendar

results_bp = Blueprint('results', __name__)

def calculate_grade(percentage):
    """Calculate grade based on percentage"""
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B'
    elif percentage >= 60:
        return 'C'
    elif percentage >= 50:
        return 'D'
    else:
        return 'F'

@results_bp.route('', methods=['GET'])
@login_required
def get_monthly_results():
    """Get monthly results with pagination and filtering"""
    try:
        current_user = get_current_user()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        user_id = request.args.get('user_id', type=int)
        batch_id = request.args.get('batch_id', type=int)
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        query = MonthlyResult.query
        
        # Filter based on user role
        if current_user.role == UserRole.STUDENT:
            # Students can only see their own results
            query = query.filter(MonthlyResult.user_id == current_user.id)
        elif user_id and current_user.role in [UserRole.TEACHER, UserRole.SUPER_USER]:
            query = query.filter(MonthlyResult.user_id == user_id)
        
        # Filter by batch
        if batch_id:
            if current_user.role == UserRole.STUDENT and not check_batch_access(current_user, batch_id):
                return error_response('Access denied to this batch', 403)
            query = query.filter(MonthlyResult.batch_id == batch_id)
        
        # Filter by month/year
        if month and year:
            query = query.filter(
                MonthlyResult.month == month,
                MonthlyResult.year == year
            )
        elif year:
            query = query.filter(MonthlyResult.year == year)
        
        # Join with user and batch for additional info
        query = query.join(User).join(Batch)
        
        # Order by calculation date
        query = query.order_by(MonthlyResult.calculated_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        results = []
        for result in pagination.items:
            result_data = {
                'id': result.id,
                'month': result.month,
                'year': result.year,
                'month_name': calendar.month_name[result.month],
                'total_exams': result.total_exams,
                'total_marks': result.total_marks,
                'obtained_marks': result.obtained_marks,
                'percentage': result.percentage,
                'grade': result.grade,
                'rank': result.rank,
                'attendance_percentage': result.attendance_percentage,
                'fee_status': result.fee_status,
                'remarks': result.remarks,
                'calculated_at': result.calculated_at.isoformat()
            }
            
            # Add user and batch information
            result_data['user'] = {
                'id': result.user.id,
                'phone': result.user.phone,
                'full_name': result.user.full_name
            }
            
            result_data['batch'] = {
                'id': result.batch.id,
                'name': result.batch.name
            }
            
            results.append(result_data)
        
        return paginated_response(
            results, 
            page, 
            per_page, 
            pagination.total, 
            "Monthly results retrieved successfully"
        )
        
    except Exception as e:
        return error_response(f'Failed to retrieve monthly results: {str(e)}', 500)

@results_bp.route('/calculate', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def calculate_monthly_results():
    """Calculate monthly results for a batch"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Required fields
        required_fields = ['batch_id', 'month', 'year']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        batch_id = data['batch_id']
        month = data['month']
        year = data['year']
        
        # Validate inputs
        if not (1 <= month <= 12):
            return error_response('Month must be between 1 and 12', 400)
        
        if year < 2020 or year > 2030:
            return error_response('Year must be between 2020 and 2030', 400)
        
        # Validate batch
        batch = Batch.query.filter_by(id=batch_id, is_active=True).first()
        if not batch:
            return error_response('Batch not found', 404)
        
        # Get all students in batch
        students = User.query.filter(
            User.role == UserRole.STUDENT,
            User.is_active == True
        ).join(User.batches).filter(Batch.id == batch_id).all()
        
        if not students:
            return error_response('No active students found in this batch', 404)
        
        # Calculate date range for the month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
        calculated_results = []
        
        for student in students:
            # Check if result already exists
            existing_result = MonthlyResult.query.filter_by(
                user_id=student.id,
                batch_id=batch_id,
                month=month,
                year=year
            ).first()
            
            # Get exam submissions for the month
            exam_submissions = db.session.query(ExamSubmission).join(
                ExamSubmission.exam
            ).filter(
                ExamSubmission.user_id == student.id,
                ExamSubmission.status == 'submitted',
                func.date(ExamSubmission.submitted_at) >= start_date,
                func.date(ExamSubmission.submitted_at) <= end_date
            ).join(
                ExamSubmission.exam.batches.any(Batch.id == batch_id)
            ).all()
            
            # Calculate exam statistics
            total_exams = len(exam_submissions)
            total_marks = sum(submission.total_marks for submission in exam_submissions)
            obtained_marks = sum(submission.obtained_marks for submission in exam_submissions)
            exam_percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
            
            # Calculate attendance for the month
            attendance_records = Attendance.query.filter(
                Attendance.user_id == student.id,
                Attendance.batch_id == batch_id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            ).all()
            
            if attendance_records:
                present_count = len([a for a in attendance_records if a.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE]])
                attendance_percentage = (present_count / len(attendance_records) * 100)
            else:
                attendance_percentage = 0
            
            # Check fee status for the month
            fee_records = Fee.query.filter(
                Fee.user_id == student.id,
                Fee.batch_id == batch_id,
                extract('month', Fee.due_date) == month,
                extract('year', Fee.due_date) == year
            ).all()
            
            if fee_records:
                paid_fees = [f for f in fee_records if f.status == FeeStatus.PAID]
                fee_status = 'paid' if len(paid_fees) == len(fee_records) else 'pending'
            else:
                fee_status = 'no_fees'
            
            # Calculate grade
            grade = calculate_grade(exam_percentage)
            
            # Generate remarks
            remarks = []
            if exam_percentage >= 90:
                remarks.append('Excellent performance')
            elif exam_percentage >= 80:
                remarks.append('Very good performance')
            elif exam_percentage >= 70:
                remarks.append('Good performance')
            elif exam_percentage >= 60:
                remarks.append('Satisfactory performance')
            elif exam_percentage < 50:
                remarks.append('Needs improvement')
            
            if attendance_percentage < 75:
                remarks.append('Poor attendance')
            elif attendance_percentage >= 95:
                remarks.append('Excellent attendance')
            
            if fee_status == 'pending':
                remarks.append('Fees pending')
            
            remarks_text = '; '.join(remarks) if remarks else None
            
            # Create or update monthly result
            if existing_result:
                existing_result.total_exams = total_exams
                existing_result.total_marks = total_marks
                existing_result.obtained_marks = obtained_marks
                existing_result.percentage = round(exam_percentage, 2)
                existing_result.grade = grade
                existing_result.attendance_percentage = round(attendance_percentage, 2)
                existing_result.fee_status = fee_status
                existing_result.remarks = remarks_text
                existing_result.calculated_at = datetime.utcnow()
                result = existing_result
            else:
                result = MonthlyResult(
                    user_id=student.id,
                    batch_id=batch_id,
                    month=month,
                    year=year,
                    total_exams=total_exams,
                    total_marks=total_marks,
                    obtained_marks=obtained_marks,
                    percentage=round(exam_percentage, 2),
                    grade=grade,
                    attendance_percentage=round(attendance_percentage, 2),
                    fee_status=fee_status,
                    remarks=remarks_text
                )
                db.session.add(result)
            
            calculated_results.append(result)
        
        # Calculate ranks based on percentage
        calculated_results.sort(key=lambda x: x.percentage, reverse=True)
        
        current_rank = 1
        prev_percentage = None
        
        for i, result in enumerate(calculated_results):
            if prev_percentage is not None and result.percentage < prev_percentage:
                current_rank = i + 1
            result.rank = current_rank
            prev_percentage = result.percentage
        
        db.session.commit()
        
        result_summary = {
            'batch_id': batch_id,
            'batch_name': batch.name,
            'month': month,
            'year': year,
            'month_name': calendar.month_name[month],
            'total_students': len(calculated_results),
            'calculated_at': datetime.utcnow().isoformat()
        }
        
        return success_response(
            f'Monthly results calculated for {len(calculated_results)} students', 
            {'summary': result_summary}, 
            201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to calculate monthly results: {str(e)}', 500)

@results_bp.route('/batch/<int:batch_id>/ranking', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_batch_ranking(batch_id):
    """Get ranking for a batch in a specific month"""
    try:
        # Validate batch
        batch = Batch.query.filter_by(id=batch_id, is_active=True).first()
        if not batch:
            return error_response('Batch not found', 404)
        
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not month or not year:
            # Default to current month
            now = datetime.now()
            month = month or now.month
            year = year or now.year
        
        # Get monthly results for the batch
        results = MonthlyResult.query.filter(
            MonthlyResult.batch_id == batch_id,
            MonthlyResult.month == month,
            MonthlyResult.year == year
        ).join(User).order_by(MonthlyResult.rank).all()
        
        if not results:
            return error_response(f'No results found for {calendar.month_name[month]} {year}', 404)
        
        ranking_data = []
        for result in results:
            rank_data = {
                'rank': result.rank,
                'student_id': result.user.id,
                'student_name': result.user.full_name,
                'student_phone': result.user.phone,
                'total_exams': result.total_exams,
                'total_marks': result.total_marks,
                'obtained_marks': result.obtained_marks,
                'percentage': result.percentage,
                'grade': result.grade,
                'attendance_percentage': result.attendance_percentage,
                'fee_status': result.fee_status
            }
            ranking_data.append(rank_data)
        
        summary = {
            'batch_id': batch_id,
            'batch_name': batch.name,
            'month': month,
            'year': year,
            'month_name': calendar.month_name[month],
            'total_students': len(ranking_data),
            'top_performer': ranking_data[0] if ranking_data else None,
            'class_average': round(sum(r['percentage'] for r in ranking_data) / len(ranking_data), 2) if ranking_data else 0
        }
        
        return success_response('Batch ranking retrieved', {
            'ranking': ranking_data,
            'summary': summary
        })
        
    except Exception as e:
        return error_response(f'Failed to get batch ranking: {str(e)}', 500)

@results_bp.route('/my-results', methods=['GET'])
@login_required
@require_role(UserRole.STUDENT)
def get_my_results():
    """Get current student's monthly results"""
    try:
        current_user = get_current_user()
        
        batch_id = request.args.get('batch_id', type=int)
        year = request.args.get('year', type=int)
        
        query = MonthlyResult.query.filter(MonthlyResult.user_id == current_user.id)
        
        # Filter by batch
        if batch_id:
            if not check_batch_access(current_user, batch_id):
                return error_response('Access denied to this batch', 403)
            query = query.filter(MonthlyResult.batch_id == batch_id)
        
        # Filter by year
        if year:
            query = query.filter(MonthlyResult.year == year)
        
        # Join with batch and order by month/year
        query = query.join(Batch).order_by(
            MonthlyResult.year.desc(),
            MonthlyResult.month.desc()
        )
        
        results = query.all()
        
        # Prepare results data
        results_data = []
        for result in results:
            result_data = {
                'id': result.id,
                'month': result.month,
                'year': result.year,
                'month_name': calendar.month_name[result.month],
                'total_exams': result.total_exams,
                'total_marks': result.total_marks,
                'obtained_marks': result.obtained_marks,
                'percentage': result.percentage,
                'grade': result.grade,
                'rank': result.rank,
                'attendance_percentage': result.attendance_percentage,
                'fee_status': result.fee_status,
                'remarks': result.remarks,
                'batch': {
                    'id': result.batch.id,
                    'name': result.batch.name
                },
                'calculated_at': result.calculated_at.isoformat()
            }
            results_data.append(result_data)
        
        # Calculate overall statistics
        if results_data:
            avg_percentage = sum(r['percentage'] for r in results_data) / len(results_data)
            best_performance = max(results_data, key=lambda x: x['percentage'])
            avg_attendance = sum(r['attendance_percentage'] for r in results_data) / len(results_data)
        else:
            avg_percentage = 0
            best_performance = None
            avg_attendance = 0
        
        summary = {
            'total_months': len(results_data),
            'average_percentage': round(avg_percentage, 2),
            'best_performance': best_performance,
            'average_attendance': round(avg_attendance, 2)
        }
        
        return success_response('Student results retrieved', {
            'results': results_data,
            'summary': summary
        })
        
    except Exception as e:
        return error_response(f'Failed to get student results: {str(e)}', 500)

@results_bp.route('/analytics', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_results_analytics():
    """Get comprehensive results analytics"""
    try:
        batch_id = request.args.get('batch_id', type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        base_query = MonthlyResult.query.filter(MonthlyResult.year == year)
        
        if batch_id:
            batch = Batch.query.filter_by(id=batch_id, is_active=True).first()
            if not batch:
                return error_response('Batch not found', 404)
            base_query = base_query.filter(MonthlyResult.batch_id == batch_id)
        
        # Monthly performance trends
        monthly_stats = db.session.query(
            MonthlyResult.month,
            func.avg(MonthlyResult.percentage).label('avg_percentage'),
            func.avg(MonthlyResult.attendance_percentage).label('avg_attendance'),
            func.count(MonthlyResult.id).label('student_count')
        ).filter(
            MonthlyResult.year == year
        )
        
        if batch_id:
            monthly_stats = monthly_stats.filter(MonthlyResult.batch_id == batch_id)
        
        monthly_stats = monthly_stats.group_by(MonthlyResult.month).order_by(MonthlyResult.month).all()
        
        monthly_trends = []
        for stat in monthly_stats:
            monthly_trends.append({
                'month': stat.month,
                'month_name': calendar.month_name[stat.month],
                'avg_percentage': round(float(stat.avg_percentage), 2),
                'avg_attendance': round(float(stat.avg_attendance), 2),
                'student_count': stat.student_count
            })
        
        # Grade distribution
        grade_distribution = db.session.query(
            MonthlyResult.grade,
            func.count(MonthlyResult.id).label('count')
        ).filter(MonthlyResult.year == year)
        
        if batch_id:
            grade_distribution = grade_distribution.filter(MonthlyResult.batch_id == batch_id)
        
        grade_distribution = grade_distribution.group_by(MonthlyResult.grade).all()
        
        grade_stats = [{'grade': grade.grade, 'count': grade.count} for grade in grade_distribution]
        
        # Top performers
        top_performers = base_query.join(User).order_by(
            MonthlyResult.percentage.desc()
        ).limit(10).all()
        
        top_performers_data = []
        for result in top_performers:
            top_performers_data.append({
                'student_name': result.user.full_name,
                'batch_name': result.batch.name if result.batch else 'Unknown',
                'month': calendar.month_name[result.month],
                'percentage': result.percentage,
                'grade': result.grade,
                'rank': result.rank
            })
        
        # Overall statistics
        total_results = base_query.count()
        avg_performance = base_query.with_entities(func.avg(MonthlyResult.percentage)).scalar() or 0
        avg_attendance = base_query.with_entities(func.avg(MonthlyResult.attendance_percentage)).scalar() or 0
        
        analytics = {
            'year': year,
            'batch_id': batch_id,
            'total_results': total_results,
            'average_performance': round(float(avg_performance), 2),
            'average_attendance': round(float(avg_attendance), 2),
            'monthly_trends': monthly_trends,
            'grade_distribution': grade_stats,
            'top_performers': top_performers_data
        }
        
        return success_response('Results analytics retrieved', {'analytics': analytics})
        
    except Exception as e:
        return error_response(f'Failed to get results analytics: {str(e)}', 500)