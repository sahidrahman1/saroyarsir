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
        
        # Filter by batch
        if batch_id:
            query = query.join(exam_batches).filter(exam_batches.c.batch_id == batch_id)
        
        # Filter by status
        if status and status in [s.value for s in ExamStatus]:
            query = query.filter(Exam.status == ExamStatus(status))
        
        # Filter by exam type
        if exam_type and exam_type in [t.value for t in ExamType]:
            query = query.filter(Exam.exam_type == ExamType(exam_type))
        
        # Search filter
        if search:
            search_filter = or_(
                Exam.title.ilike(f'%{search}%'),
                Exam.description.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Order by start time
        query = query.order_by(Exam.start_time.desc())
        
        exams = []
        for exam in query.all():
            exam_data = serialize_exam(exam)
            
            # Add student-specific information
            if current_user.role == UserRole.STUDENT:
                submission = ExamSubmission.query.filter_by(
                    exam_id=exam.id,
                    user_id=current_user.id
                ).first()
                
                exam_data['isSubmitted'] = submission is not None
                exam_data['submissionStatus'] = submission.status.value if submission else None
                exam_data['obtainedMarks'] = submission.obtained_marks if submission else None
                exam_data['submittedAt'] = submission.submitted_at.isoformat() if submission and submission.submitted_at else None
            
            exams.append(exam_data)
        
        return success_response('Exams retrieved successfully', exams)
        
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
        required_fields = ['title', 'examType', 'duration', 'startTime', 'endTime', 'batchIds']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        # Validate dates
        try:
            start_time = datetime.fromisoformat(data['startTime'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data['endTime'].replace('Z', '+00:00'))
        except ValueError:
            return error_response('Invalid date format for startTime or endTime', 400)
        
        if end_time <= start_time:
            return error_response('End time must be after start time', 400)
        
        # Validate exam type
        try:
            exam_type = ExamType(data['examType'])
        except ValueError:
            return error_response('Invalid exam type', 400)
        
        # Validate batch IDs
        batch_ids = data['batchIds']
        if not batch_ids or not isinstance(batch_ids, list):
            return error_response('At least one batch ID is required', 400)
        
        batches = Batch.query.filter(Batch.id.in_(batch_ids)).all()
        if len(batches) != len(batch_ids):
            return error_response('One or more batch IDs are invalid', 400)
        
        current_user = get_current_user()
        
        # Create new exam
        exam = Exam(
            title=data['title'].strip(),
            description=data.get('description', '').strip() if data.get('description') else None,
            exam_type=exam_type,
            total_marks=int(data.get('totalMarks', 0)),
            pass_marks=int(data.get('passMarks', 0)),
            duration=int(data['duration']),
            start_time=start_time,
            end_time=end_time,
            instructions=data.get('instructions', '').strip() if data.get('instructions') else None,
            status=ExamStatus(data.get('status', 'active')),
            created_by=current_user.id,
            allow_review=data.get('allowReview', True),
            shuffle_questions=data.get('shuffleQuestions', False),
            show_results_immediately=data.get('showResultsImmediately', True)
        )
        
        # Add batches
        exam.batches.extend(batches)
        
        db.session.add(exam)
        db.session.flush()  # Get the exam ID
        
        # Add questions if provided
        questions_data = data.get('questions', [])
        for q_data in questions_data:
            question = Question(
                exam_id=exam.id,
                question_type=QuestionType(q_data.get('type', 'mcq')),
                question_text=q_data['questionText'],
                options=json.dumps(q_data.get('options', [])) if q_data.get('options') else None,
                correct_answer=q_data.get('correctAnswer', ''),
                marks=int(q_data.get('marks', 1)),
                explanation=q_data.get('explanation', ''),
                order_number=q_data.get('orderNumber', 0)
            )
            db.session.add(question)
        
        db.session.commit()
        
        exam_data = serialize_exam(exam, include_questions=True)
        
        return success_response('Exam created successfully', exam_data, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create exam: {str(e)}', 500)

@exams_bp.route('/<int:exam_id>', methods=['PUT'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def update_exam(exam_id):
    """Update an existing exam"""
    try:
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return error_response('Exam not found', 404)
        
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Update allowed fields
        updatable_fields = ['title', 'description', 'duration', 'startTime', 'endTime', 
                           'totalMarks', 'passMarks', 'instructions', 'status', 
                           'allowReview', 'shuffleQuestions', 'showResultsImmediately']
        
        for field in updatable_fields:
            if field in data:
                if field in ['startTime', 'endTime']:
                    try:
                        setattr(exam, field.replace('Time', '_time'), 
                               datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                    except ValueError:
                        return error_response(f'Invalid {field} format', 400)
                elif field == 'status':
                    try:
                        setattr(exam, field, ExamStatus(data[field]))
                    except ValueError:
                        return error_response('Invalid status', 400)
                elif field in ['totalMarks', 'passMarks', 'duration']:
                    setattr(exam, field.replace('M', '_m').replace('D', '_d').lower(), int(data[field]))
                else:
                    snake_case_field = ''.join(['_' + c.lower() if c.isupper() else c for c in field]).lstrip('_')
                    setattr(exam, snake_case_field, data[field])
        
        # Update batch assignments if provided
        if 'batchIds' in data:
            batch_ids = data['batchIds']
            batches = Batch.query.filter(Batch.id.in_(batch_ids)).all()
            if len(batches) != len(batch_ids):
                return error_response('One or more batch IDs are invalid', 400)
            
            exam.batches.clear()
            exam.batches.extend(batches)
        
        exam.updated_at = datetime.utcnow()
        db.session.commit()
        
        exam_data = serialize_exam(exam, include_questions=True)
        
        return success_response('Exam updated successfully', exam_data)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update exam: {str(e)}', 500)

@exams_bp.route('/<int:exam_id>', methods=['DELETE'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def delete_exam(exam_id):
    """Delete an exam (soft delete by deactivating)"""
    try:
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return error_response('Exam not found', 404)
        
        # Check if exam has submissions
        submissions_count = ExamSubmission.query.filter_by(exam_id=exam_id).count()
        if submissions_count > 0:
            # Soft delete by deactivating
            exam.status = ExamStatus.INACTIVE
            exam.updated_at = datetime.utcnow()
        else:
            # Hard delete if no submissions
            db.session.delete(exam)
        
        db.session.commit()
        
        return success_response('Exam deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete exam: {str(e)}', 500)

@exams_bp.route('/monthly', methods=['GET'])
@login_required
def get_monthly_exams():
    """Get monthly exams for current month or specified month"""
    try:
        current_user = get_current_user()
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        batch_id = request.args.get('batch_id', type=int)
        
        # Validate month and year
        if not (1 <= month <= 12):
            return error_response('Invalid month. Must be between 1 and 12', 400)
        
        # Get start and end of month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        query = Exam.query.filter(
            Exam.start_time >= start_date,
            Exam.start_time <= end_date
        )
        
        # Filter based on user role
        if current_user.role == UserRole.STUDENT:
            # Students can only see exams for their batches
            user_batch_ids = [b.id for b in current_user.batches if b.is_active]
            if user_batch_ids:
                query = query.join(exam_batches).filter(exam_batches.c.batch_id.in_(user_batch_ids))
            else:
                return success_response('No monthly exams found', [])
        elif batch_id:
            query = query.join(exam_batches).filter(exam_batches.c.batch_id == batch_id)
        
        monthly_exams = query.order_by(Exam.start_time).all()
        
        exams_data = []
        for exam in monthly_exams:
            exam_data = serialize_exam(exam)
            
            # Add submission info for students
            if current_user.role == UserRole.STUDENT:
                submission = ExamSubmission.query.filter_by(
                    exam_id=exam.id,
                    user_id=current_user.id
                ).first()
                
                exam_data['isSubmitted'] = submission is not None
                exam_data['submissionStatus'] = submission.status.value if submission else None
                exam_data['obtainedMarks'] = submission.obtained_marks if submission else None
            
            exams_data.append(exam_data)
        
        return success_response('Monthly exams retrieved successfully', {
            'year': year,
            'month': month,
            'exams': exams_data
        })
        
    except Exception as e:
        return error_response(f'Failed to retrieve monthly exams: {str(e)}', 500)
        if current_user.role == UserRole.STUDENT:
            user_batch_ids = [b.id for b in current_user.batches if b.is_active]
            exam_batch_ids = [b.id for b in exam.batches]
            
            if not any(bid in user_batch_ids for bid in exam_batch_ids):
                return error_response('Access denied to this exam', 403)
        
        exam_data = serialize_exam(exam, include_questions=True)
        
        # Add student-specific information
        if current_user.role == UserRole.STUDENT:
            submission = ExamSubmission.query.filter_by(
                exam_id=exam.id,
                user_id=current_user.id
            ).first()
            
            exam_data['submission_status'] = submission.status.value if submission else None
            exam_data['submission_id'] = submission.id if submission else None
            exam_data['can_attempt'] = (
                exam.status == ExamStatus.ACTIVE and
                datetime.utcnow() >= exam.start_time and
                datetime.utcnow() <= exam.end_time and
                not submission
            )
            exam_data['can_review'] = (
                exam.allow_review and
                submission and
                submission.status == SubmissionStatus.SUBMITTED
            )
            
            # Hide correct answers from students unless they can review
            if not exam_data.get('can_review', False):
                for question in exam_data.get('questions', []):
                    question.pop('correct_answer', None)
                    question.pop('explanation', None)
        
        return success_response('Exam details retrieved', {'exam': exam_data})
        
    except Exception as e:
        return error_response(f'Failed to get exam: {str(e)}', 500)


@exams_bp.route('/<int:exam_id>', methods=['PUT'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def update_exam(exam_id):
    """Update exam information"""
    try:
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return error_response('Exam not found', 404)
        
        # Check if exam has submissions
        has_submissions = ExamSubmission.query.filter_by(exam_id=exam_id).first() is not None
        
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Prevent certain updates if exam has submissions
        restricted_fields = ['duration', 'total_marks', 'pass_marks']
        if has_submissions:
            for field in restricted_fields:
                if field in data and data[field] != getattr(exam, field):
                    return error_response(f'Cannot update {field} after students have started taking the exam', 400)
        
        # Update allowed fields
        updatable_fields = ['title', 'description', 'start_time', 'end_time', 'instructions', 
                           'status', 'allow_review', 'shuffle_questions', 'show_results_immediately']
        
        if not has_submissions:
            updatable_fields.extend(restricted_fields)
        
        for field in updatable_fields:
            if field in data:
                if field in ['start_time', 'end_time']:
                    try:
                        datetime_val = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                        setattr(exam, field, datetime_val)
                    except ValueError:
                        return error_response(f'Invalid {field} format', 400)
                elif field == 'status':
                    try:
                        setattr(exam, field, ExamStatus(data[field]))
                    except ValueError:
                        return error_response('Invalid exam status', 400)
                else:
                    setattr(exam, field, data[field])
        
        # Validate date range
        if exam.end_time <= exam.start_time:
            return error_response('End time must be after start time', 400)
        
        # Update batch associations
        if 'batch_ids' in data:
            batch_ids = data['batch_ids']
            batches = Batch.query.filter(Batch.id.in_(batch_ids), Batch.is_active == True).all()
            if len(batches) != len(batch_ids):
                return error_response('Some batch IDs are invalid', 400)
            
            exam.batches.clear()
            exam.batches.extend(batches)
        
        exam.updated_at = datetime.utcnow()
        db.session.commit()
        
        exam_data = serialize_exam(exam)
        
        return success_response('Exam updated successfully', {'exam': exam_data})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update exam: {str(e)}', 500)

@exams_bp.route('/<int:exam_id>', methods=['DELETE'])
@login_required
@require_role(UserRole.SUPER_USER)
def delete_exam(exam_id):
    """Delete an exam (only if no submissions)"""
    try:
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return error_response('Exam not found', 404)
        
        # Check if exam has submissions
        has_submissions = ExamSubmission.query.filter_by(exam_id=exam_id).first() is not None
        
        if has_submissions:
            return error_response('Cannot delete exam with submissions. Deactivate instead.', 400)
        
        # Delete associated questions first
        Question.query.filter_by(exam_id=exam_id).delete()
        
        # Clear batch associations
        exam.batches.clear()
        
        # Delete exam
        db.session.delete(exam)
        db.session.commit()
        
        return success_response('Exam deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete exam: {str(e)}', 500)

@exams_bp.route('/<int:exam_id>/start', methods=['POST'])
@login_required
@require_role(UserRole.STUDENT)
def start_exam(exam_id):
    """Start an exam attempt"""
    try:
        current_user = get_current_user()
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return error_response('Exam not found', 404)
        
        # Check access permissions
        user_batch_ids = [b.id for b in current_user.batches if b.is_active]
        exam_batch_ids = [b.id for b in exam.batches]
        
        if not any(bid in user_batch_ids for bid in exam_batch_ids):
            return error_response('Access denied to this exam', 403)
        
        # Check exam status and timing
        if exam.status != ExamStatus.ACTIVE:
            return error_response('Exam is not active', 400)
        
        current_time = datetime.utcnow()
        if current_time < exam.start_time:
            return error_response('Exam has not started yet', 400)
        
        if current_time > exam.end_time:
            return error_response('Exam has ended', 400)
        
        # Check if student already has a submission
        existing_submission = ExamSubmission.query.filter_by(
            exam_id=exam_id,
            user_id=current_user.id
        ).first()
        
        if existing_submission:
            return error_response('You have already attempted this exam', 409)
        
        # Create new submission
        submission = ExamSubmission(
            exam_id=exam_id,
            user_id=current_user.id,
            started_at=current_time,
            total_marks=exam.total_marks,
            status=SubmissionStatus.IN_PROGRESS,
            ip_address=request.environ.get('REMOTE_ADDR'),
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(submission)
        db.session.commit()
        
        # Get exam questions (shuffled if required)
        questions = Question.query.filter_by(exam_id=exam_id, is_active=True).all()
        
        if exam.shuffle_questions:
            import random
            questions = random.sample(questions, len(questions))
        else:
            questions = sorted(questions, key=lambda q: q.order_index)
        
        # Prepare questions for student (without correct answers)
        questions_data = []
        for question in questions:
            question_data = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type.value,
                'marks': question.marks,
                'options': question.options if question.question_type == QuestionType.MCQ else None,
                'order_index': question.order_index
            }
            questions_data.append(question_data)
        
        submission_data = serialize_submission(submission)
        submission_data['questions'] = questions_data
        submission_data['time_remaining'] = exam.duration * 60  # Convert to seconds
        
        return success_response('Exam started successfully', {'submission': submission_data})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to start exam: {str(e)}', 500)

@exams_bp.route('/<int:exam_id>/submit', methods=['POST'])
@login_required
@require_role(UserRole.STUDENT)
def submit_exam(exam_id):
    """Submit exam answers"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Get submission
        submission = ExamSubmission.query.filter_by(
            exam_id=exam_id,
            user_id=current_user.id,
            status=SubmissionStatus.IN_PROGRESS
        ).first()
        
        if not submission:
            return error_response('No active exam submission found', 404)
        
        exam = submission.exam
        answers_data = data.get('answers', [])
        
        # Process answers
        total_obtained_marks = 0
        
        for answer_data in answers_data:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer_text', '').strip()
            
            if not question_id:
                continue
            
            question = Question.query.get(question_id)
            if not question or question.exam_id != exam_id:
                continue
            
            # Check if answer already exists
            existing_answer = ExamAnswer.query.filter_by(
                submission_id=submission.id,
                question_id=question_id
            ).first()
            
            if existing_answer:
                existing_answer.answer_text = answer_text
                existing_answer.answered_at = datetime.utcnow()
                answer = existing_answer
            else:
                answer = ExamAnswer(
                    submission_id=submission.id,
                    question_id=question_id,
                    user_id=current_user.id,
                    answer_text=answer_text
                )
                db.session.add(answer)
            
            # Check if answer is correct
            is_correct = False
            marks_obtained = 0
            
            if question.question_type == QuestionType.MCQ:
                # For MCQ, check exact match with correct answer
                is_correct = answer_text.strip().lower() == question.correct_answer.strip().lower()
                marks_obtained = question.marks if is_correct else 0
            elif question.question_type == QuestionType.WRITTEN:
                # For written questions, manual marking would be needed
                # For now, we'll give full marks if answer is provided
                is_correct = bool(answer_text.strip())
                marks_obtained = question.marks if is_correct else 0
            
            answer.is_correct = is_correct
            answer.marks_obtained = marks_obtained
            total_obtained_marks += marks_obtained
        
        # Update submission
        submission.submitted_at = datetime.utcnow()
        submission.obtained_marks = total_obtained_marks
        submission.percentage = (total_obtained_marks / submission.total_marks * 100) if submission.total_marks > 0 else 0
        submission.status = SubmissionStatus.SUBMITTED
        
        # Calculate time taken
        time_taken = (submission.submitted_at - submission.started_at).total_seconds() / 60  # minutes
        submission.time_taken = int(time_taken)
        
        db.session.commit()
        
        # Prepare result data
        result_data = {
            'submission_id': submission.id,
            'total_marks': submission.total_marks,
            'obtained_marks': submission.obtained_marks,
            'percentage': round(submission.percentage, 2),
            'pass_marks': exam.pass_marks,
            'passed': submission.obtained_marks >= exam.pass_marks,
            'time_taken': submission.time_taken,
            'submitted_at': submission.submitted_at.isoformat()
        }
        
        # Add detailed answers if review is allowed
        if exam.allow_review and exam.show_results_immediately:
            answers = []
            for answer in submission.answers:
                answer_data = {
                    'question_id': answer.question_id,
                    'question_text': answer.question.question_text,
                    'question_type': answer.question.question_type.value,
                    'user_answer': answer.answer_text,
                    'correct_answer': answer.question.correct_answer,
                    'is_correct': answer.is_correct,
                    'marks_obtained': answer.marks_obtained,
                    'total_marks': answer.question.marks,
                    'explanation': answer.question.explanation
                }
                answers.append(answer_data)
            
            result_data['answers'] = answers
        
        return success_response('Exam submitted successfully', {'result': result_data})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to submit exam: {str(e)}', 500)

@exams_bp.route('/<int:exam_id>/submissions', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_exam_submissions(exam_id):
    """Get all submissions for an exam"""
    try:
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return error_response('Exam not found', 404)
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        query = ExamSubmission.query.filter_by(exam_id=exam_id)
        
        # Order by submission time
        query = query.order_by(ExamSubmission.submitted_at.desc().nullslast(), 
                               ExamSubmission.started_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        submissions = []
        for submission in pagination.items:
            submission_data = serialize_submission(submission)
            
            # Add user information
            user = submission.user
            submission_data['user'] = {
                'id': user.id,
                'phone': user.phone,
                'full_name': user.full_name,
                'email': user.email
            }
            
            submissions.append(submission_data)
        
        return paginated_response(
            submissions, 
            page, 
            per_page, 
            pagination.total, 
            "Exam submissions retrieved successfully"
        )
        
    except Exception as e:
        return error_response(f'Failed to get exam submissions: {str(e)}', 500)