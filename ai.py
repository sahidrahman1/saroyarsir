"""
AI Integration Routes
Google Gemini AI for question generation and educational content
"""
from flask import Blueprint, request, jsonify
from utils.auth import login_required, require_role
from utils.response import success_response, error_response
from models import UserRole
from data.nctb_curriculum import NCTB_CURRICULUM, get_subjects_for_class, get_chapters_for_subject, get_available_classes
import asyncio
import logging

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger(__name__)

@ai_bp.route('/api-status', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_api_status():
    """Get current API key usage status"""
    try:
        from services.praggo_ai import (
            GEMINI_API_KEYS, key_usage_count, key_failures, 
            MAX_DAILY_REQUESTS, reset_daily_usage_if_needed
        )
        
        # Reset counters if needed
        reset_daily_usage_if_needed()
        
        status = []
        for i, key in enumerate(GEMINI_API_KEYS):
            masked_key = key[:10] + '...' + key[-4:] if len(key) > 14 else key[:8] + '...'
            usage = key_usage_count.get(i, 0)
            failures = key_failures.get(i, 0)
            
            status.append({
                'key_index': i + 1,
                'masked_key': masked_key,
                'usage': usage,
                'max_usage': MAX_DAILY_REQUESTS,
                'usage_percentage': (usage / MAX_DAILY_REQUESTS) * 100,
                'failures': failures,
                'status': 'active' if failures < 3 and usage < MAX_DAILY_REQUESTS else 'limited'
            })
        
        return jsonify({
            'success': True,
            'api_keys': status,
            'total_keys': len(GEMINI_API_KEYS),
            'active_keys': len([s for s in status if s['status'] == 'active'])
        })
    
    except Exception as e:
        logger.error(f"API status error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@ai_bp.route('/generate-questions', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def generate_questions():
    """Generate questions using AI"""
    try:
        from services.praggo_ai import generate_questions_sync, QuestionGenerationParams
        
        data = request.get_json()
        
        # Create parameters object
        params = QuestionGenerationParams(
            class_id=data.get('class_id'),
            class_name=data.get('class_name'),
            subject_id=data.get('subject_id'),
            subject_name=data.get('subject_name'),
            chapter_id=data.get('chapter_id'),
            chapter_title=data.get('chapter_title'),
            question_type=data.get('question_type', 'mcq'),
            difficulty=data.get('difficulty', 'medium'),
            category=data.get('category', 'mixed'),
            quantity=data.get('quantity', 5)
        )
        
        # Generate questions
        questions = generate_questions_sync(params)
        
        # Convert to dict format
        questions_data = []
        for q in questions:
            question_dict = {
                'question_text': q.question_text,
                'question_type': q.question_type,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation,
                'solution': q.solution
            }
            if q.options:
                question_dict['options'] = q.options
            questions_data.append(question_dict)
        
        return success_response('Questions generated successfully', {
            'questions': questions_data,
            'count': len(questions_data)
        })
        
    except Exception as e:
        logger.error(f'Failed to generate questions: {str(e)}')
        return error_response(f'Failed to generate questions: {str(e)}', 500)

@ai_bp.route('/solve', methods=['POST'])
@login_required
def solve_with_ai():
    """Solve problems with AI assistance"""
    try:
        from services.praggo_ai import solve_with_ai_sync, AISolveParams
        
        data = request.get_json()
        
        # Create parameters object
        params = AISolveParams(
            class_id=data.get('class_id'),
            class_name=data.get('class_name'),
            subject_id=data.get('subject_id'),
            subject_name=data.get('subject_name'),
            chapter_title=data.get('chapter_title'),
            prompt=data.get('prompt', ''),
            conversation_history=data.get('conversation_history', [])
        )
        
        # Get AI solution
        solution = solve_with_ai_sync(params)
        
        return success_response('Solution generated successfully', {
            'solution': solution,
            'prompt': params.prompt
        })
        
    except Exception as e:
        logger.error(f'Failed to solve with AI: {str(e)}')
        return error_response(f'Failed to solve problem: {str(e)}', 500)

@ai_bp.route('/curriculum/classes', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_curriculum_classes():
    """Get available classes from NCTB curriculum"""
    try:
        classes = get_available_classes()
        return success_response('Classes retrieved successfully', {
            'classes': classes,
            'count': len(classes)
        })
    except Exception as e:
        logger.error(f'Failed to get classes: {str(e)}')
        return error_response(f'Failed to get classes: {str(e)}', 500)

@ai_bp.route('/curriculum/subjects/<class_name>', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_curriculum_subjects(class_name):
    """Get available subjects for a class"""
    try:
        subjects = get_subjects_for_class(class_name)
        if not subjects:
            return error_response(f'No subjects found for {class_name}', 404)
        
        return success_response('Subjects retrieved successfully', {
            'class': class_name,
            'subjects': subjects,
            'count': len(subjects)
        })
    except Exception as e:
        logger.error(f'Failed to get subjects for {class_name}: {str(e)}')
        return error_response(f'Failed to get subjects: {str(e)}', 500)

@ai_bp.route('/curriculum/chapters/<class_name>/<subject_name>', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_curriculum_chapters(class_name, subject_name):
    """Get available chapters for a subject in a class"""
    try:
        chapters = get_chapters_for_subject(class_name, subject_name)
        if not chapters:
            return error_response(f'No chapters found for {subject_name} in {class_name}', 404)
        
        return success_response('Chapters retrieved successfully', {
            'class': class_name,
            'subject': subject_name,
            'chapters': chapters,
            'count': len(chapters)
        })
    except Exception as e:
        logger.error(f'Failed to get chapters for {class_name} {subject_name}: {str(e)}')
        return error_response(f'Failed to get chapters: {str(e)}', 500)

@ai_bp.route('/curriculum/full', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_full_curriculum():
    """Get complete NCTB curriculum structure"""
    try:
        return success_response('Full curriculum retrieved successfully', {
            'curriculum': NCTB_CURRICULUM,
            'total_classes': len(NCTB_CURRICULUM)
        })
    except Exception as e:
        logger.error(f'Failed to get full curriculum: {str(e)}')
        return error_response(f'Failed to get curriculum: {str(e)}', 500)

@ai_bp.route('/health', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def ai_health():
    """Check AI service health"""
    try:
        try:
            import google.generativeai as genai
        except ImportError:
            import mock_google_genai as genai
        import os
        
        # Test API key configuration
        api_key = os.getenv('GEMINI_KEY_1') or os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            return error_response('AI service not configured - no API key', 503)
        
        # Test AI connection
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'Hello' if you're working.")
        
        if response.text:
            return success_response('AI service is healthy', {
                'service': 'Google Gemini',
                'model': 'gemini-pro',
                'status': 'active',
                'response_preview': response.text[:50] + '...' if len(response.text) > 50 else response.text
            })
        else:
            return error_response('AI service not responding', 503)
            
    except Exception as e:
        logger.error(f'AI health check failed: {str(e)}')
        return error_response(f'AI health check failed: {str(e)}', 503)