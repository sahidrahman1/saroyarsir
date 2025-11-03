"""
Question Builder Routes
Question creation, AI integration, and question management
"""
from flask import Blueprint, request
from models import db, Question, Exam, QuestionType, UserRole
from utils.auth import login_required, require_role, get_current_user
from utils.response import success_response, error_response, serialize_question
from datetime import datetime
try:
    import google.generativeai as genai
except ImportError:
    import mock_google_genai as genai
import json
import re
import os

questions_bp = Blueprint('questions', __name__)

# Configure Google AI
def configure_ai():
    """Configure Google Generative AI"""
    api_key = os.environ.get('GOOGLE_AI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

@questions_bp.route('/exam/<int:exam_id>', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_exam_questions(exam_id):
    """Get all questions for an exam"""
    try:
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return error_response('Exam not found', 404)
        
        questions = Question.query.filter_by(
            exam_id=exam_id, 
            is_active=True
        ).order_by(Question.order_index, Question.id).all()
        
        questions_data = [serialize_question(question, include_correct_answer=True) for question in questions]
        
        return success_response('Exam questions retrieved', {'questions': questions_data})
        
    except Exception as e:
        return error_response(f'Failed to get exam questions: {str(e)}', 500)

@questions_bp.route('/<int:question_id>', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_question(question_id):
    """Get specific question details"""
    try:
        question = Question.query.get(question_id)
        
        if not question:
            return error_response('Question not found', 404)
        
        question_data = serialize_question(question, include_correct_answer=True)
        
        return success_response('Question details retrieved', {'question': question_data})
        
    except Exception as e:
        return error_response(f'Failed to get question: {str(e)}', 500)

@questions_bp.route('', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def create_question():
    """Create a new question"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Required fields
        required_fields = ['exam_id', 'question_text', 'correct_answer']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        # Validate exam
        exam = Exam.query.get(data['exam_id'])
        if not exam:
            return error_response('Exam not found', 404)
        
        # Validate question type
        question_type = QuestionType.MCQ
        if data.get('question_type'):
            try:
                question_type = QuestionType(data['question_type'])
            except ValueError:
                return error_response('Invalid question type', 400)
        
        # Validate marks
        marks = data.get('marks', 1)
        if not isinstance(marks, int) or marks <= 0:
            return error_response('Marks must be a positive integer', 400)
        
        # Validate options for MCQ
        options = None
        if question_type == QuestionType.MCQ:
            options = data.get('options', [])
            if not options or len(options) < 2:
                return error_response('MCQ questions must have at least 2 options', 400)
            
            # Check if correct answer is in options
            correct_answer = data['correct_answer'].strip()
            if correct_answer not in options:
                return error_response('Correct answer must be one of the options', 400)
        
        # Get next order index
        max_order = db.session.query(db.func.max(Question.order_index)).filter_by(
            exam_id=data['exam_id']
        ).scalar() or 0
        
        # Create new question
        question = Question(
            exam_id=data['exam_id'],
            question_text=data['question_text'].strip(),
            question_type=question_type,
            marks=marks,
            options=options,
            correct_answer=data['correct_answer'].strip(),
            explanation=data.get('explanation', '').strip() if data.get('explanation') else None,
            order_index=data.get('order_index', max_order + 1)
        )
        
        db.session.add(question)
        
        # Update exam total marks
        exam.total_marks += marks
        
        db.session.commit()
        
        question_data = serialize_question(question, include_correct_answer=True)
        
        return success_response('Question created successfully', {'question': question_data}, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create question: {str(e)}', 500)

@questions_bp.route('/<int:question_id>', methods=['PUT'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def update_question(question_id):
    """Update question information"""
    try:
        question = Question.query.get(question_id)
        
        if not question:
            return error_response('Question not found', 404)
        
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Store old marks for exam total calculation
        old_marks = question.marks
        
        # Update allowed fields
        updatable_fields = ['question_text', 'question_type', 'marks', 'options', 
                           'correct_answer', 'explanation', 'order_index']
        
        for field in updatable_fields:
            if field in data:
                if field == 'question_type':
                    try:
                        new_type = QuestionType(data[field])
                        question.question_type = new_type
                        
                        # Clear options if changing to written
                        if new_type == QuestionType.WRITTEN:
                            question.options = None
                    except ValueError:
                        return error_response('Invalid question type', 400)
                elif field == 'marks':
                    marks = data[field]
                    if not isinstance(marks, int) or marks <= 0:
                        return error_response('Marks must be a positive integer', 400)
                    question.marks = marks
                elif field == 'options':
                    if question.question_type == QuestionType.MCQ:
                        options = data[field]
                        if not options or len(options) < 2:
                            return error_response('MCQ questions must have at least 2 options', 400)
                        question.options = options
                elif field == 'correct_answer':
                    correct_answer = data[field].strip()
                    if question.question_type == QuestionType.MCQ and question.options:
                        if correct_answer not in question.options:
                            return error_response('Correct answer must be one of the options', 400)
                    question.correct_answer = correct_answer
                else:
                    setattr(question, field, data[field])
        
        # Update exam total marks if question marks changed
        if old_marks != question.marks:
            exam = question.exam
            exam.total_marks = exam.total_marks - old_marks + question.marks
        
        db.session.commit()
        
        question_data = serialize_question(question, include_correct_answer=True)
        
        return success_response('Question updated successfully', {'question': question_data})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update question: {str(e)}', 500)

@questions_bp.route('/<int:question_id>', methods=['DELETE'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def delete_question(question_id):
    """Delete a question"""
    try:
        question = Question.query.get(question_id)
        
        if not question:
            return error_response('Question not found', 404)
        
        # Check if exam has submissions
        from models import ExamSubmission
        has_submissions = ExamSubmission.query.filter_by(exam_id=question.exam_id).first() is not None
        
        if has_submissions:
            return error_response('Cannot delete question from exam with submissions', 400)
        
        # Update exam total marks
        exam = question.exam
        exam.total_marks -= question.marks
        
        # Delete question
        db.session.delete(question)
        db.session.commit()
        
        return success_response('Question deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete question: {str(e)}', 500)

@questions_bp.route('/bulk', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def create_bulk_questions():
    """Create multiple questions at once"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        exam_id = data.get('exam_id')
        questions_data = data.get('questions', [])
        
        if not exam_id:
            return error_response('Exam ID is required', 400)
        
        if not questions_data:
            return error_response('Questions data is required', 400)
        
        # Validate exam
        exam = Exam.query.get(exam_id)
        if not exam:
            return error_response('Exam not found', 404)
        
        # Get next order index
        max_order = db.session.query(db.func.max(Question.order_index)).filter_by(
            exam_id=exam_id
        ).scalar() or 0
        
        created_questions = []
        total_marks_added = 0
        
        for i, question_data in enumerate(questions_data):
            # Validate required fields
            if not question_data.get('question_text') or not question_data.get('correct_answer'):
                return error_response(f'Question {i+1}: Missing question_text or correct_answer', 400)
            
            # Validate question type
            question_type = QuestionType.MCQ
            if question_data.get('question_type'):
                try:
                    question_type = QuestionType(question_data['question_type'])
                except ValueError:
                    return error_response(f'Question {i+1}: Invalid question type', 400)
            
            # Validate marks
            marks = question_data.get('marks', 1)
            if not isinstance(marks, int) or marks <= 0:
                return error_response(f'Question {i+1}: Marks must be a positive integer', 400)
            
            # Validate options for MCQ
            options = None
            if question_type == QuestionType.MCQ:
                options = question_data.get('options', [])
                if not options or len(options) < 2:
                    return error_response(f'Question {i+1}: MCQ questions must have at least 2 options', 400)
                
                correct_answer = question_data['correct_answer'].strip()
                if correct_answer not in options:
                    return error_response(f'Question {i+1}: Correct answer must be one of the options', 400)
            
            # Create question
            question = Question(
                exam_id=exam_id,
                question_text=question_data['question_text'].strip(),
                question_type=question_type,
                marks=marks,
                options=options,
                correct_answer=question_data['correct_answer'].strip(),
                explanation=question_data.get('explanation', '').strip() if question_data.get('explanation') else None,
                order_index=max_order + i + 1
            )
            
            db.session.add(question)
            created_questions.append(question)
            total_marks_added += marks
        
        # Update exam total marks
        exam.total_marks += total_marks_added
        
        db.session.commit()
        
        questions_data_response = [serialize_question(q, include_correct_answer=True) for q in created_questions]
        
        return success_response(
            f'{len(created_questions)} questions created successfully', 
            {'questions': questions_data_response}, 
            201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create bulk questions: {str(e)}', 500)

@questions_bp.route('/ai-generate', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def ai_generate_questions():
    """Generate questions using AI based on NCTB syllabus"""
    try:
        if not configure_ai():
            return error_response('AI service not configured', 503)
        
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Required fields
        required_fields = ['class_level', 'subject', 'chapter', 'question_count']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        class_level = data['class_level']
        subject = data['subject']
        chapter = data['chapter']
        question_count = data['question_count']
        question_type = data.get('question_type', 'mcq')
        difficulty = data.get('difficulty', 'medium')
        marks_per_question = data.get('marks_per_question', 1)
        
        # Validate inputs
        if not isinstance(question_count, int) or question_count <= 0 or question_count > 20:
            return error_response('Question count must be between 1 and 20', 400)
        
        if class_level not in ['6', '7', '8', '9', '10']:
            return error_response('Class level must be between 6 and 10', 400)
        
        if question_type not in ['mcq', 'written']:
            return error_response('Question type must be "mcq" or "written"', 400)
        
        if difficulty not in ['easy', 'medium', 'hard']:
            return error_response('Difficulty must be "easy", "medium", or "hard"', 400)
        
        # Create AI prompt
        prompt = create_ai_prompt(class_level, subject, chapter, question_count, question_type, difficulty)
        
        try:
            # Generate questions using Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            if not response.text:
                return error_response('AI service did not return any content', 503)
            
            # Parse AI response
            questions = parse_ai_response(response.text, question_type, marks_per_question)
            
            if not questions:
                return error_response('Failed to parse AI-generated questions', 503)
            
            return success_response(
                f'{len(questions)} questions generated successfully', 
                {'questions': questions}
            )
            
        except Exception as ai_error:
            return error_response(f'AI generation failed: {str(ai_error)}', 503)
        
    except Exception as e:
        return error_response(f'Failed to generate questions: {str(e)}', 500)

def create_ai_prompt(class_level, subject, chapter, question_count, question_type, difficulty):
    """Create AI prompt for question generation"""
    
    difficulty_descriptions = {
        'easy': 'basic recall and simple understanding',
        'medium': 'application and analysis',
        'hard': 'critical thinking and complex problem solving'
    }
    
    if question_type == 'mcq':
        format_instruction = """
Format each question as JSON:
{
    "question_text": "The question text here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Brief explanation of why this answer is correct"
}

Return only a JSON array of questions, no additional text.
"""
    else:
        format_instruction = """
Format each question as JSON:
{
    "question_text": "The question text here",
    "correct_answer": "Expected answer or key points",
    "explanation": "Marking scheme or answer guidelines"
}

Return only a JSON array of questions, no additional text.
"""
    
    prompt = f"""
Generate {question_count} {difficulty} level {question_type.upper()} questions for Class {class_level} {subject}, Chapter: {chapter}.

Requirements:
- Follow Bangladesh NCTB curriculum and syllabus
- Questions should test {difficulty_descriptions[difficulty]}
- Use proper Bengali/English terminology as appropriate for the subject
- Questions should be clear, unambiguous, and age-appropriate
- For MCQ: Provide 4 options with only one correct answer
- Avoid overly complex language
- Ensure questions align with learning objectives for Class {class_level}

{format_instruction}
"""
    
    return prompt

def parse_ai_response(ai_text, question_type, marks_per_question):
    """Parse AI response and extract questions"""
    try:
        # Clean the response text
        cleaned_text = ai_text.strip()
        
        # Remove any markdown code blocks
        cleaned_text = re.sub(r'```(?:json)?\s*', '', cleaned_text)
        cleaned_text = re.sub(r'```\s*$', '', cleaned_text)
        
        # Try to find JSON array in the text
        json_match = re.search(r'\[.*\]', cleaned_text, re.DOTALL)
        if json_match:
            cleaned_text = json_match.group(0)
        
        # Parse JSON
        questions_data = json.loads(cleaned_text)
        
        if not isinstance(questions_data, list):
            return None
        
        questions = []
        for q_data in questions_data:
            if not isinstance(q_data, dict):
                continue
            
            question = {
                'question_text': q_data.get('question_text', '').strip(),
                'question_type': question_type,
                'marks': marks_per_question,
                'correct_answer': q_data.get('correct_answer', '').strip(),
                'explanation': q_data.get('explanation', '').strip()
            }
            
            if question_type == 'mcq':
                options = q_data.get('options', [])
                if len(options) >= 2:
                    question['options'] = options
                else:
                    continue  # Skip invalid MCQ questions
            
            if question['question_text'] and question['correct_answer']:
                questions.append(question)
        
        return questions
        
    except json.JSONDecodeError:
        return None
    except Exception:
        return None

@questions_bp.route('/reorder', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def reorder_questions():
    """Reorder questions in an exam"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        exam_id = data.get('exam_id')
        question_orders = data.get('question_orders', [])
        
        if not exam_id:
            return error_response('Exam ID is required', 400)
        
        if not question_orders:
            return error_response('Question orders are required', 400)
        
        # Validate exam
        exam = Exam.query.get(exam_id)
        if not exam:
            return error_response('Exam not found', 404)
        
        # Update question orders
        for item in question_orders:
            question_id = item.get('question_id')
            order_index = item.get('order_index')
            
            if question_id and order_index is not None:
                question = Question.query.filter_by(id=question_id, exam_id=exam_id).first()
                if question:
                    question.order_index = order_index
        
        db.session.commit()
        
        return success_response('Questions reordered successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to reorder questions: {str(e)}', 500)