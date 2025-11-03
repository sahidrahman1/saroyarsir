"""
Enhanced Online Exam System Routes
Auto-submission, time tracking, result calculation, and multi-language support
"""
from flask import Blueprint, request, jsonify, session
from models import (db, Exam, Question, ExamSubmission, ExamAnswer, Batch, User, 
                   UserRole, ExamType, ExamStatus, SubmissionStatus, QuestionType, 
                   exam_batches, QuestionBank)
from utils.auth import login_required, require_role, get_current_user
from utils.response import success_response, error_response, serialize_exam
from services.sms_service import send_exam_notification
from services.praggo_ai import generate_questions_sync, QuestionGenerationParams
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

online_exams_bp = Blueprint('online_exams', __name__)

@online_exams_bp.route('/available', methods=['GET'])
@login_required
def get_available_exams():
    """Get available online exams for current student"""
    try:
        current_user = get_current_user()
        
        if current_user.role != UserRole.STUDENT:
            return error_response('Only students can access this endpoint', 403)
        
        # Get student's batches
        user_batch_ids = [b.id for b in current_user.batches if b.is_active]
        if not user_batch_ids:
            return success_response('No exams available', [])
        
        # Get active exams
        now = datetime.utcnow()
        exams = (Exam.query
                .join(exam_batches)
                .filter(
                    exam_batches.c.batch_id.in_(user_batch_ids),
                    Exam.exam_type == ExamType.ONLINE,
                    Exam.status == ExamStatus.ACTIVE,
                    Exam.start_time <= now,
                    Exam.end_time >= now
                )
                .order_by(Exam.start_time)
                .all())
        
        exam_list = []
        for exam in exams:
            # Check if student has already submitted
            submission = ExamSubmission.query.filter_by(
                exam_id=exam.id,
                user_id=current_user.id
            ).first()
            
            exam_data = serialize_exam(exam)
            exam_data.update({
                'can_take': not submission,
                'submission_status': submission.status.value if submission else None,
                'time_remaining': max(0, int((exam.end_time - now).total_seconds() / 60)),
                'questions_count': len(exam.questions),
                'is_started': bool(submission and submission.status == SubmissionStatus.IN_PROGRESS)
            })
            
            exam_list.append(exam_data)
        
        return success_response('Available exams retrieved', exam_list)
        
    except Exception as e:
        logger.error(f"Error getting available exams: {e}")
        return error_response(f'Failed to retrieve exams: {str(e)}', 500)

@online_exams_bp.route('/<int:exam_id>/start', methods=['POST'])
@login_required
def start_exam(exam_id):
    """Start an online exam"""
    try:
        current_user = get_current_user()
        
        if current_user.role != UserRole.STUDENT:
            return error_response('Only students can take exams', 403)
        
        # Get exam
        exam = Exam.query.get(exam_id)
        if not exam:
            return error_response('Exam not found', 404)
        
        # Check if exam is available
        now = datetime.utcnow()
        if exam.status != ExamStatus.ACTIVE:
            return error_response('Exam is not active', 400)
        
        if now < exam.start_time:
            return error_response('Exam has not started yet', 400)
        
        if now > exam.end_time:
            return error_response('Exam has ended', 400)
        
        # Check if student is enrolled in exam batches
        user_batch_ids = [b.id for b in current_user.batches if b.is_active]
        exam_batch_ids = [b.id for b in exam.batches]
        
        if not set(user_batch_ids).intersection(set(exam_batch_ids)):
            return error_response('You are not enrolled in this exam', 403)
        
        # Check if already submitted
        existing_submission = ExamSubmission.query.filter_by(
            exam_id=exam_id,
            user_id=current_user.id
        ).first()
        
        if existing_submission:
            if existing_submission.status == SubmissionStatus.SUBMITTED:
                return error_response('You have already submitted this exam', 400)
            
            # Resume existing submission
            exam_data = serialize_exam(exam)
            exam_data.update({
                'submission_id': existing_submission.id,
                'started_at': existing_submission.started_at.isoformat(),
                'time_remaining': max(0, exam.duration - existing_submission.time_taken),
                'questions': [serialize_question_for_exam(q) for q in exam.questions if q.is_active]
            })
            
            # Get existing answers
            answers = ExamAnswer.query.filter_by(
                submission_id=existing_submission.id
            ).all()
            
            exam_data['existing_answers'] = {
                str(answer.question_id): answer.answer_text for answer in answers
            }
            
            return success_response('Exam resumed', exam_data)
        
        # Create new submission
        submission = ExamSubmission(
            exam_id=exam_id,
            user_id=current_user.id,
            started_at=now,
            status=SubmissionStatus.IN_PROGRESS,
            total_marks=exam.total_marks,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(submission)
        db.session.commit()
        
        # Prepare exam data
        exam_data = serialize_exam(exam)
        exam_data.update({
            'submission_id': submission.id,
            'started_at': submission.started_at.isoformat(),
            'time_remaining': exam.duration,
            'questions': [serialize_question_for_exam(q) for q in exam.questions if q.is_active]
        })
        
        # Shuffle questions if enabled
        if exam.shuffle_questions:
            import random
            random.shuffle(exam_data['questions'])
        
        return success_response('Exam started successfully', exam_data)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error starting exam: {e}")
        return error_response(f'Failed to start exam: {str(e)}', 500)

@online_exams_bp.route('/<int:exam_id>/submit-answer', methods=['POST'])
@login_required
def submit_answer(exam_id):
    """Submit answer for a specific question"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        if not data or 'question_id' not in data or 'answer' not in data:
            return error_response('Question ID and answer are required', 400)
        
        question_id = data['question_id']
        answer_text = data['answer']
        
        # Get submission
        submission = ExamSubmission.query.filter_by(
            exam_id=exam_id,
            user_id=current_user.id,
            status=SubmissionStatus.IN_PROGRESS
        ).first()
        
        if not submission:
            return error_response('No active submission found', 404)
        
        # Check if exam time is up
        exam = submission.exam
        elapsed_time = int((datetime.utcnow() - submission.started_at).total_seconds() / 60)
        
        if elapsed_time >= exam.duration:
            # Auto-submit exam
            return auto_submit_exam(submission)
        
        # Get question
        question = Question.query.filter_by(
            id=question_id,
            exam_id=exam_id,
            is_active=True
        ).first()
        
        if not question:
            return error_response('Question not found', 404)
        
        # Update or create answer
        existing_answer = ExamAnswer.query.filter_by(
            submission_id=submission.id,
            question_id=question_id
        ).first()
        
        if existing_answer:
            existing_answer.answer_text = answer_text
            existing_answer.answered_at = datetime.utcnow()
        else:
            answer = ExamAnswer(
                submission_id=submission.id,
                question_id=question_id,
                user_id=current_user.id,
                answer_text=answer_text
            )
            db.session.add(answer)
        
        # Update submission time
        submission.time_taken = elapsed_time
        
        db.session.commit()
        
        return success_response('Answer saved successfully', {
            'time_remaining': max(0, exam.duration - elapsed_time)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error submitting answer: {e}")
        return error_response(f'Failed to save answer: {str(e)}', 500)

@online_exams_bp.route('/<int:exam_id>/submit', methods=['POST'])
@login_required
def submit_exam(exam_id):
    """Submit exam for evaluation"""
    try:
        current_user = get_current_user()
        
        # Get submission
        submission = ExamSubmission.query.filter_by(
            exam_id=exam_id,
            user_id=current_user.id,
            status=SubmissionStatus.IN_PROGRESS
        ).first()
        
        if not submission:
            return error_response('No active submission found', 404)
        
        return finalize_exam_submission(submission)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error submitting exam: {e}")
        return error_response(f'Failed to submit exam: {str(e)}', 500)

def auto_submit_exam(submission):
    """Auto-submit exam when time is up"""
    try:
        return finalize_exam_submission(submission, auto_submitted=True)
    except Exception as e:
        logger.error(f"Error auto-submitting exam: {e}")
        return error_response('Failed to auto-submit exam', 500)

def finalize_exam_submission(submission, auto_submitted=False):
    """Finalize and evaluate exam submission"""
    try:
        exam = submission.exam
        
        # Update submission status
        submission.status = SubmissionStatus.SUBMITTED
        submission.submitted_at = datetime.utcnow()
        
        if not auto_submitted:
            elapsed_time = int((submission.submitted_at - submission.started_at).total_seconds() / 60)
            submission.time_taken = min(elapsed_time, exam.duration)
        else:
            submission.time_taken = exam.duration
        
        # Calculate marks
        total_marks = 0
        obtained_marks = 0
        
        answers = ExamAnswer.query.filter_by(submission_id=submission.id).all()
        
        for answer in answers:
            question = answer.question
            total_marks += question.marks
            
            # Auto-evaluate MCQ questions
            if question.question_type == QuestionType.MCQ:
                if answer.answer_text.strip().lower() == question.correct_answer.strip().lower():
                    answer.is_correct = True
                    answer.marks_obtained = question.marks
                    obtained_marks += question.marks
                else:
                    answer.is_correct = False
                    answer.marks_obtained = 0
            else:
                # Written questions need manual evaluation
                answer.marks_obtained = 0  # Will be set during manual evaluation
        
        submission.total_marks = total_marks
        submission.obtained_marks = obtained_marks
        submission.percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
        
        db.session.commit()
        
        # Prepare result data
        result_data = {
            'submission_id': submission.id,
            'total_marks': total_marks,
            'obtained_marks': obtained_marks,
            'percentage': round(submission.percentage, 2),
            'passed': submission.percentage >= (exam.pass_marks / exam.total_marks * 100),
            'time_taken': submission.time_taken,
            'auto_submitted': auto_submitted,
            'submitted_at': submission.submitted_at.isoformat()
        }
        
        # Show results immediately if enabled
        if exam.show_results_immediately:
            result_data['detailed_results'] = get_exam_results(submission)
        
        return success_response(
            'Exam submitted successfully' + (' (auto-submitted)' if auto_submitted else ''),
            result_data
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error finalizing submission: {e}")
        raise

@online_exams_bp.route('/<int:exam_id>/results', methods=['GET'])
@login_required
def get_exam_result(exam_id):
    """Get exam results for student"""
    try:
        current_user = get_current_user()
        
        submission = ExamSubmission.query.filter_by(
            exam_id=exam_id,
            user_id=current_user.id,
            status=SubmissionStatus.SUBMITTED
        ).first()
        
        if not submission:
            return error_response('No submission found', 404)
        
        exam = submission.exam
        
        # Check if results are available
        if not exam.show_results_immediately and current_user.role == UserRole.STUDENT:
            return error_response('Results not yet available', 403)
        
        results = get_exam_results(submission)
        return success_response('Results retrieved successfully', results)
        
    except Exception as e:
        logger.error(f"Error getting exam results: {e}")
        return error_response(f'Failed to retrieve results: {str(e)}', 500)

def get_exam_results(submission):
    """Get detailed exam results"""
    exam = submission.exam
    answers = ExamAnswer.query.filter_by(submission_id=submission.id).all()
    
    question_results = []
    for answer in answers:
        question = answer.question
        question_results.append({
            'question_id': question.id,
            'question_text': question.question_text,
            'question_type': question.question_type.value,
            'marks': question.marks,
            'user_answer': answer.answer_text,
            'correct_answer': question.correct_answer,
            'is_correct': answer.is_correct,
            'marks_obtained': answer.marks_obtained,
            'explanation': question.explanation if exam.allow_review else None
        })
    
    return {
        'exam_title': exam.title,
        'total_marks': submission.total_marks,
        'obtained_marks': submission.obtained_marks,
        'percentage': round(submission.percentage, 2),
        'passed': submission.percentage >= (exam.pass_marks / exam.total_marks * 100),
        'time_taken': submission.time_taken,
        'submitted_at': submission.submitted_at.isoformat(),
        'questions': question_results
    }

@online_exams_bp.route('/create-with-ai', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def create_exam_with_ai():
    """Create exam with AI-generated questions"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Create exam first
        exam_data = {
            'title': data.get('title'),
            'description': data.get('description', ''),
            'duration': data.get('duration', 60),
            'start_time': data.get('start_time'),
            'end_time': data.get('end_time'),
            'batch_ids': data.get('batch_ids', [])
        }
        
        # Create exam using existing logic
        exam = create_basic_exam(exam_data)
        
        # Generate questions with AI
        ai_params = QuestionGenerationParams(
            class_id=data.get('class_id', ''),
            class_name=data.get('class_name', ''),
            subject_id=data.get('subject_id', ''),
            subject_name=data.get('subject_name', ''),
            chapter_id=data.get('chapter_id'),
            chapter_title=data.get('chapter_title'),
            question_type=data.get('question_type', 'mcq'),
            difficulty=data.get('difficulty', 'medium'),
            category=data.get('category', 'mixed'),
            quantity=data.get('quantity', 5)
        )
        
        generated_questions = generate_questions_sync(ai_params)
        
        # Add questions to exam
        total_marks = 0
        for i, gen_q in enumerate(generated_questions):
            question = Question(
                exam_id=exam.id,
                question_text=gen_q.question_text,
                question_type=QuestionType.MCQ if gen_q.question_type == 'MCQ' else QuestionType.WRITTEN,
                marks=data.get('marks_per_question', 5),
                options=gen_q.options,
                correct_answer=gen_q.correct_answer,
                explanation=gen_q.explanation,
                order_index=i + 1
            )
            db.session.add(question)
            total_marks += question.marks
        
        exam.total_marks = total_marks
        exam.status = ExamStatus.ACTIVE
        
        db.session.commit()
        
        return success_response('AI-powered exam created successfully', {
            'exam': serialize_exam(exam),
            'questions_generated': len(generated_questions)
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating AI exam: {e}")
        return error_response(f'Failed to create AI exam: {str(e)}', 500)

def create_basic_exam(exam_data):
    """Helper function to create basic exam"""
    # Parse dates
    start_time = datetime.fromisoformat(exam_data['start_time'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(exam_data['end_time'].replace('Z', '+00:00'))
    
    exam = Exam(
        title=exam_data['title'],
        description=exam_data['description'],
        exam_type=ExamType.ONLINE,
        duration=exam_data['duration'],
        start_time=start_time,
        end_time=end_time,
        status=ExamStatus.DRAFT,
        created_by=get_current_user().id
    )
    
    db.session.add(exam)
    db.session.flush()
    
    # Add batch associations
    for batch_id in exam_data['batch_ids']:
        batch = Batch.query.get(batch_id)
        if batch:
            exam.batches.append(batch)
    
    return exam

def serialize_question_for_exam(question):
    """Serialize question for exam taking (hide correct answer)"""
    return {
        'id': question.id,
        'question_text': question.question_text,
        'question_type': question.question_type.value,
        'marks': question.marks,
        'options': question.options if question.question_type == QuestionType.MCQ else None,
        'order_index': question.order_index
    }

@online_exams_bp.route('/<int:exam_id>/notify-students', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def notify_students(exam_id):
    """Send SMS notification to students about exam"""
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return error_response('Exam not found', 404)
        
        # Get all students from exam batches
        students = []
        for batch in exam.batches:
            students.extend([s for s in batch.students if s.role == UserRole.STUDENT and s.is_active])
        
        # Remove duplicates
        unique_students = list({s.id: s for s in students}.values())
        
        if not unique_students:
            return error_response('No students found for this exam', 400)
        
        # Send notifications
        results = send_exam_notification(exam, unique_students)
        
        successful_count = sum(1 for r in results if r.success)
        
        return success_response(
            f'Notifications sent to {successful_count}/{len(unique_students)} students',
            {
                'total_students': len(unique_students),
                'successful_notifications': successful_count,
                'failed_notifications': len(unique_students) - successful_count
            }
        )
        
    except Exception as e:
        logger.error(f"Error sending notifications: {e}")
        return error_response(f'Failed to send notifications: {str(e)}', 500)