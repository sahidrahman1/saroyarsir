"""
Praggo AI Service - Python Implementation
Google Gemini AI integration for question generation and problem solving
"""
import os
import re
import json
import asyncio
from typing import List, Dict, Optional, AsyncGenerator, Tuple
try:
    import google.generativeai as genai
except ImportError:
    import mock_google_genai as genai
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Praggo AI - 5-key rotation system for high availability
GEMINI_API_KEYS = [
    'AIzaSyDWvMAsRMrJZQaQSTZfLv_THVt_g9QJeGQ',  # Primary key provided by user
    os.getenv('GEMINI_KEY_2', ''),
    os.getenv('GEMINI_KEY_3', ''),
    os.getenv('GEMINI_KEY_4', ''),
    os.getenv('GEMINI_KEY_5', ''),
]

# Filter out empty keys but ensure we have at least the first one
GEMINI_API_KEYS = [key for key in GEMINI_API_KEYS if key] or ['AIzaSyDWvMAsRMrJZQaQSTZfLv_THVt_g9QJeGQ']

current_key_index = 0
key_failures = {}  # Track failures per key
key_usage_count = {}  # Track daily usage per key
key_last_reset = {}  # Track when usage was last reset
MAX_DAILY_REQUESTS = 1000  # Estimated daily limit per key

def reset_daily_usage_if_needed():
    """Reset daily usage counters if it's a new day"""
    import datetime
    today = datetime.date.today()
    
    for key_index in range(len(GEMINI_API_KEYS)):
        last_reset = key_last_reset.get(key_index)
        if not last_reset or last_reset < today:
            key_usage_count[key_index] = 0
            key_last_reset[key_index] = today

def get_next_api_key() -> Tuple[str, int]:
    """Get the next available API key using rotation system with usage tracking"""
    global current_key_index
    
    # Reset usage counters if needed
    reset_daily_usage_if_needed()
    
    start_index = current_key_index
    
    # Try each key, considering failures and usage limits
    while True:
        failures = key_failures.get(current_key_index, 0)
        usage = key_usage_count.get(current_key_index, 0)
        
        # If this key hasn't failed recently and hasn't exceeded daily limit
        if failures < 3 and usage < MAX_DAILY_REQUESTS:
            key = GEMINI_API_KEYS[current_key_index]
            index = current_key_index
            
            # Increment usage counter
            key_usage_count[index] = usage + 1
            
            # Move to next key for next request
            current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
            
            logger.info(f"Using API key {index + 1}/{len(GEMINI_API_KEYS)} (Usage: {usage + 1}/{MAX_DAILY_REQUESTS})")
            return key, index
        
        # Move to next key
        current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
        
        # If we've tried all keys, reset failures and try again
        if current_key_index == start_index:
            # Check if all keys are at their limit
            all_at_limit = all(
                key_usage_count.get(i, 0) >= MAX_DAILY_REQUESTS 
                for i in range(len(GEMINI_API_KEYS))
            )
            
            if all_at_limit:
                logger.error("All API keys have reached their daily limit")
                raise Exception("সকল API কী দৈনিক সীমা অতিক্রম করেছে। আগামীকাল আবার চেষ্টা করুন।")
            
            # Reset failures if all keys have failed
            key_failures.clear()
            logger.info("Reset all key failures, retrying...")
            continue

def mark_key_failure(key_index: int):
    """Mark a key as failed"""
    failures = key_failures.get(key_index, 0)
    key_failures[key_index] = failures + 1

def mark_key_success(key_index: int):
    """Mark a key as successful"""
    if key_index in key_failures:
        del key_failures[key_index]

@dataclass
class QuestionGenerationParams:
    class_id: str
    class_name: str
    subject_id: str
    subject_name: str
    chapter_id: Optional[str] = None
    chapter_title: Optional[str] = None
    question_type: str = 'mcq'  # mcq, cq, creative
    difficulty: str = 'medium'  # easy, medium, hard, mixed
    category: str = 'mixed'  # math, theory, mixed
    quantity: int = 5

@dataclass
class GeneratedQuestion:
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str = ''
    explanation: str = ''
    solution: str = ''

@dataclass
class AISolveParams:
    class_id: str
    class_name: str
    subject_id: str
    subject_name: str
    chapter_title: Optional[str] = None
    prompt: str = ''
    conversation_history: Optional[List[Dict[str, str]]] = None

async def generate_questions(params: QuestionGenerationParams) -> List[GeneratedQuestion]:
    """Generate questions using Google Gemini AI"""
    key, index = get_next_api_key()
    
    try:
        # Configure Gemini
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = build_question_prompt(params)
        
        response = await asyncio.to_thread(model.generate_content, prompt)
        text = response.text
        
        # Parse the response to extract questions
        questions = parse_questions(text, params.question_type)
        
        mark_key_success(index)
        return questions
        
    except Exception as error:
        logger.error(f"Gemini API error with key {index + 1}: {str(error)}")
        mark_key_failure(index)
        
        # If quota exceeded or rate limit, try next key
        error_msg = str(error).lower()
        if 'quota' in error_msg or 'rate' in error_msg:
            if len(GEMINI_API_KEYS) > 1:
                logger.info('Retrying with next API key...')
                return await generate_questions(params)  # Retry with next key
        
        raise Exception('সকল API কী ব্যর্থ হয়েছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।')

async def solve_with_ai(params: AISolveParams) -> AsyncGenerator[str, None]:
    """Solve problems with AI using streaming response"""
    key, index = get_next_api_key()
    
    try:
        # Configure Gemini
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        system_prompt = build_solver_prompt(params)
        
        # Build conversation history
        history = params.conversation_history or []
        
        # For streaming, we'll simulate it with a complete response
        # In production, you might want to use the actual streaming API
        full_prompt = f"{system_prompt}\n\nপ্রশ্ন: {params.prompt}"
        
        response = await asyncio.to_thread(model.generate_content, full_prompt)
        text = response.text
        
        # Simulate streaming by yielding chunks
        chunk_size = 50
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            yield chunk
            await asyncio.sleep(0.1)  # Small delay to simulate streaming
        
        mark_key_success(index)
        
    except Exception as error:
        logger.error(f"Gemini AI solve error with key {index + 1}: {str(error)}")
        mark_key_failure(index)
        
        error_msg = str(error).lower()
        if 'quota' in error_msg or 'rate' in error_msg:
            if len(GEMINI_API_KEYS) > 1:
                logger.info('Retrying with next API key...')
                async for chunk in solve_with_ai(params):
                    yield chunk
                return
        
        raise Exception('AI সেবা বর্তমানে উপলব্ধ নেই। অনুগ্রহ করে পরে আবার চেষ্টা করুন।')

def build_question_prompt(params: QuestionGenerationParams) -> str:
    """Build the prompt for question generation"""
    question_formats = {
        'mcq': """
Format each MCQ question as follows:
প্রশ্ন: [Question text in Bangla]
ক) [Option A]
খ) [Option B]
গ) [Option C]
ঘ) [Option D]
সঠিক উত্তর: [ক/খ/গ/ঘ]
ব্যাখ্যা: [Detailed explanation in Bangla]
সমাধান: [Step-by-step solution if mathematical]

---
""",
        'cq': """
Format each CQ (Creative Question) as:
প্রশ্ন: [Question text in Bangla]
উত্তর: [Detailed answer with explanation in Bangla]
সমাধান: [Step-by-step solution in Bangla]

---
""",
        'creative': """
Format each Creative Question as:
উদ্দীপক: [Stimulus/Context in Bangla - real-life scenario]
প্রশ্ন ক) [Knowledge-based question - মনে রাখার প্রশ্ন]
প্রশ্ন খ) [Comprehension question - বুঝার প্রশ্ন]
প্রশ্ন গ) [Application question - প্রয়োগের প্রশ্ন]
প্রশ্ন ঘ) [Analysis/Synthesis question - বিশ্লেষণ/সৃজনশীল প্রশ্ন]

উত্তর ক) [Answer in Bangla]
উত্তর খ) [Answer in Bangla]
উত্তর গ) [Answer in Bangla]
উত্তর ঘ) [Answer in Bangla]

---
"""
    }
    
    format_text = question_formats.get(params.question_type, question_formats['mcq'])
    
    # Build subject-specific guidelines
    subject_guidelines = ""
    if 'গণিত' in params.subject_name or 'Math' in params.subject_name:
        subject_guidelines = """
MATHEMATICS SPECIFIC GUIDELINES:
- Include calculation-based questions
- Show step-by-step mathematical solutions
- Use proper mathematical notation in Bangla
- Include word problems relevant to Bangladeshi context
- For geometry: include diagrams descriptions
- For algebra: show each algebraic step clearly
"""
    elif 'বিজ্ঞান' in params.subject_name or 'Science' in params.subject_name:
        subject_guidelines = """
SCIENCE SPECIFIC GUIDELINES:
- Include practical examples from daily life in Bangladesh
- Relate concepts to local environment and context
- Include questions about scientific processes and experiments
- Use proper scientific terminology in Bangla
- Include cause-effect relationships
- Connect theory with real-world applications
"""
    
    # Build chapter-specific context
    chapter_context = ""
    if params.chapter_title:
        chapter_context = f"""
CHAPTER FOCUS: {params.chapter_title}
- Focus specifically on topics covered in this chapter
- Use terminology and concepts from this chapter
- Reference chapter-specific examples and applications
"""
    
    prompt = f"""You are an expert NCTB (National Curriculum and Textbook Board of Bangladesh) question generator with deep knowledge of Bangladeshi education system.

Generate {params.quantity} {params.question_type.upper()} questions for:
- Class: {params.class_name} (শ্রেণি: {params.class_name})
- Subject: {params.subject_name} (বিষয়: {params.subject_name})
{f"- Chapter: {params.chapter_title} (অধ্যায়: {params.chapter_title})" if params.chapter_title else ""}
- Question Type: {params.question_type} (প্রশ্নের ধরন: {params.question_type})
- Difficulty: {params.difficulty} (কঠিনতা: {params.difficulty})

NCTB CURRICULUM COMPLIANCE:
1. All questions MUST follow NCTB curriculum standards for Bangladesh
2. Questions should be in BANGLA (বাংলা) language only
3. Use appropriate difficulty level for the specified class
4. Include Bangladeshi context, names, places, and examples
5. Follow NCTB question pattern and marking scheme

QUESTION QUALITY REQUIREMENTS:
1. For MCQ: Provide 4 distinct options with only ONE clearly correct answer
2. Avoid negative options or "all of the above" type answers
3. Include detailed explanations that help students learn
4. For mathematical problems: show complete step-by-step solutions
5. Use clear, simple language appropriate for the class level

{subject_guidelines}

{chapter_context}

FORMATTING REQUIREMENTS:
{format_text}

Generate EXACTLY {params.quantity} questions following the format above. Each question should be educational, curriculum-aligned, and culturally relevant to Bangladeshi students. Separate each question with "---"."""

    return prompt

def build_solver_prompt(params: AISolveParams) -> str:
    """Build the prompt for AI problem solving"""
    return f"""You are Praggo AI, an expert tutor for Bangladesh's NCTB curriculum.

CONTEXT:
- Student Class: {params.class_name}
- Subject: {params.subject_name}
{f"- Current Chapter: {params.chapter_title}" if params.chapter_title else ""}

YOUR ROLE:
1. Answer student questions clearly in BANGLA (বাংলা)
2. Follow NCTB curriculum standards strictly
3. Provide step-by-step explanations for mathematical problems
4. Use simple language suitable for the student's class level
5. Encourage learning with positive reinforcement

GUIDELINES:
- Be patient and supportive
- Break down complex concepts into simple steps
- Use examples from daily life when helpful
- For math problems: show each calculation step
- For science: explain concepts with real-world applications
- Always verify answers are curriculum-appropriate

Respond in a friendly, educational manner. Start your responses with encouraging words like "চমৎকার প্রশ্ন!" or "আমি সাহায্য করছি...\""""

def parse_questions(text: str, question_type: str) -> List[GeneratedQuestion]:
    """Parse generated questions from AI response"""
    questions = []
    parts = [p.strip() for p in text.split('---') if p.strip()]
    
    for part in parts:
        try:
            if question_type == 'mcq':
                question_match = re.search(r'প্রশ্ন[:\s]*(.*?)(?=ক\))', part, re.DOTALL)
                option_a = re.search(r'ক\)\s*(.*?)(?=খ\))', part, re.DOTALL)
                option_b = re.search(r'খ\)\s*(.*?)(?=গ\))', part, re.DOTALL)
                option_c = re.search(r'গ\)\s*(.*?)(?=ঘ\))', part, re.DOTALL)
                option_d = re.search(r'ঘ\)\s*(.*?)(?=সঠিক উত্তর)', part, re.DOTALL)
                correct_answer = re.search(r'সঠিক উত্তর[:\s]*(.*?)(?=ব্যাখ্যা|$)', part, re.DOTALL)
                explanation = re.search(r'ব্যাখ্যা[:\s]*(.*?)(?=সমাধান|$)', part, re.DOTALL)
                solution = re.search(r'সমাধান[:\s]*(.*?)$', part, re.DOTALL)
                
                if all([question_match, option_a, option_b, option_c, option_d, correct_answer]):
                    questions.append(GeneratedQuestion(
                        question_text=question_match.group(1).strip(),
                        question_type='MCQ',
                        options=[
                            option_a.group(1).strip(),
                            option_b.group(1).strip(),
                            option_c.group(1).strip(),
                            option_d.group(1).strip()
                        ],
                        correct_answer=correct_answer.group(1).strip(),
                        explanation=explanation.group(1).strip() if explanation else '',
                        solution=solution.group(1).strip() if solution else ''
                    ))
            else:
                question_match = re.search(r'প্রশ্ন[:\s]*(.*?)(?=উত্তর)', part, re.DOTALL)
                answer_match = re.search(r'উত্তর[:\s]*(.*?)(?=সমাধান|$)', part, re.DOTALL)
                solution_match = re.search(r'সমাধান[:\s]*(.*?)$', part, re.DOTALL)
                
                if question_match and answer_match:
                    questions.append(GeneratedQuestion(
                        question_text=question_match.group(1).strip(),
                        question_type=question_type.upper(),
                        correct_answer=answer_match.group(1).strip(),
                        explanation=answer_match.group(1).strip(),
                        solution=solution_match.group(1).strip() if solution_match else ''
                    ))
        except Exception as error:
            logger.error(f'Error parsing question: {error}')
    
    return questions

# Sync wrapper functions for compatibility
def generate_questions_sync(params: QuestionGenerationParams) -> List[GeneratedQuestion]:
    """Synchronous wrapper for generate_questions"""
    return asyncio.run(generate_questions(params))

def solve_with_ai_sync(params: AISolveParams) -> str:
    """Synchronous wrapper for solve_with_ai"""
    async def _solve():
        result = ""
        async for chunk in solve_with_ai(params):
            result += chunk
        return result
    
    return asyncio.run(_solve())