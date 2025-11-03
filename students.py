"""
Student Management Routes
CRUD operations specifically for student management from teacher dashboard
"""
from flask import Blueprint, request, session
from flask_bcrypt import generate_password_hash
from models import db, User, UserRole, Batch, user_batches
from utils.auth import login_required, require_role, get_current_user
from utils.response import success_response, error_response, serialize_user
from sqlalchemy import or_
import re
import secrets
import string
from datetime import datetime

students_bp = Blueprint('students', __name__)

def generate_password(length=8):
    """Generate a random password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_phone(phone):
    """Validate and format phone number"""
    phone = re.sub(r'[^\d]', '', phone)
    
    if phone.startswith('880'):
        phone = phone[3:]
    elif phone.startswith('+880'):
        phone = phone[4:]
    
    if len(phone) == 11 and phone.startswith('01'):
        return phone
    
    return None

@students_bp.route('', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_students():
    """Get all students with their batch information"""
    try:
        batch_id = request.args.get('batch_id', type=int)
        search = request.args.get('search', '').strip()
        
        query = User.query.filter(User.role == UserRole.STUDENT, User.is_active == True)
        
        # Filter by batch
        if batch_id:
            query = query.join(user_batches).filter(user_batches.c.batch_id == batch_id)
        
        # Search filter
        if search:
            search_filter = or_(
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.phoneNumber.ilike(f'%{search}%'),
                User.guardian_name.ilike(f'%{search}%'),
                User.guardian_phone.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        students = query.order_by(User.first_name, User.last_name).all()
        
        students_data = []
        for student in students:
            student_data = serialize_user(student)
            # Add batch information
            if student.batches:
                student_data['batch'] = {
                    'id': student.batches[0].id,
                    'name': student.batches[0].name,
                    'description': student.batches[0].description
                }
                student_data['batchId'] = student.batches[0].id
            else:
                student_data['batch'] = None
                student_data['batchId'] = None
            
            # Format for frontend
            student_data['firstName'] = student_data.get('first_name', '')
            student_data['lastName'] = student_data.get('last_name', '')
            student_data['phoneNumber'] = student_data.get('phoneNumber', '')  # Fixed: use phoneNumber not phone
            student_data['studentId'] = student_data.get('student_id', '')
            student_data['isActive'] = student_data.get('is_active', True)
            student_data['guardianPhone'] = student_data.get('guardian_phone', '')
            student_data['guardianName'] = student_data.get('guardian_name', '')
            student_data['school'] = student_data.get('address', '')
            
            students_data.append(student_data)
        
        return success_response('Students retrieved successfully', students_data)
        
    except Exception as e:
        return error_response(f'Failed to retrieve students: {str(e)}', 500)

@students_bp.route('', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def create_student():
    """Create a new student"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Required fields
        required_fields = ['firstName', 'lastName']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        # Use guardian phone as primary phone if student phone not provided
        guardian_phone = data.get('guardianPhone', '')
        student_phone = data.get('phoneNumber', '')
        
        # Prioritize guardian phone for login
        if guardian_phone:
            # Validate guardian phone number
            phone = validate_phone(guardian_phone)
            if not phone:
                return error_response('Invalid guardian phone number format', 400)
            
            # Check if guardian phone already exists
            existing_user = User.query.filter_by(phoneNumber=phone).first()
            if existing_user:
                return error_response('User with this guardian phone number already exists', 409)
        elif student_phone:
            # Fallback to student phone if no guardian phone
            phone = validate_phone(student_phone)
            if not phone:
                return error_response('Invalid phone number format', 400)
            
            existing_user = User.query.filter_by(phoneNumber=phone).first()
            if existing_user:
                return error_response('User with this phone number already exists', 409)
        else:
            # Generate a unique placeholder phone number if no phone provided
            import random
            phone = f"0199{random.randint(1000000, 9999999)}"
        
        # Validate email if provided
        email = data.get('email')
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return error_response('Student with this email already exists', 409)
        
        # Generate student ID if not provided
        student_id = data.get('studentId')
        if not student_id:
            # Generate student ID based on current year and sequence
            current_year = datetime.now().year
            count = User.query.filter(User.role == UserRole.STUDENT).count()
            student_id = f"{current_year}{count + 1:04d}"
        
        # Create new student
        student = User(
            phoneNumber=phone,  # This will be guardian phone for login
            phone=phone,  # Set phone field to same as phoneNumber for SMS
            first_name=data['firstName'].strip(),
            last_name=data['lastName'].strip(),
            email=data.get('email', '').strip() if data.get('email') else None,
            role=UserRole.STUDENT,
            date_of_birth=datetime.strptime(data['dateOfBirth'], '%Y-%m-%d').date() if data.get('dateOfBirth') else None,
            address=data.get('school', '').strip() if data.get('school') else data.get('address', '').strip() if data.get('address') else None,
            guardian_phone=phone,  # Set guardian phone to same as phoneNumber for SMS
            guardian_name=data.get('guardianName', '').strip() if data.get('guardianName') else None,
            emergency_contact=data.get('emergencyContact', '').strip() if data.get('emergencyContact') else None,
            is_active=data.get('isActive', True)
        )
        
        # Generate unique password for student (students login with guardian phone + unique password)
        from utils.password_generator import generate_simple_unique_password
        unique_password = generate_simple_unique_password(data['firstName'], phone)
        student.password_hash = generate_password_hash(unique_password)
        
        db.session.add(student)
        db.session.flush()  # Get the student ID
        
        # Assign to batch if provided
        batch_id = data.get('batchId')
        if batch_id:
            batch = Batch.query.get(batch_id)
            if batch:
                student.batches.append(batch)
        
        db.session.commit()
        
        # Prepare response data
        student_data = serialize_user(student)
        student_data['firstName'] = student_data.get('first_name', '')
        student_data['lastName'] = student_data.get('last_name', '')
        student_data['phoneNumber'] = student_data.get('phoneNumber', '')  # Fixed: use phoneNumber not phone
        student_data['studentId'] = student_data.get('student_id', '')
        student_data['isActive'] = student_data.get('is_active', True)
        student_data['guardianPhone'] = student_data.get('guardian_phone', '')
        student_data['guardianName'] = student_data.get('guardian_name', '')
        student_data['school'] = student_data.get('address', '')
        
        if student.batches:
            student_data['batch'] = {
                'id': student.batches[0].id,
                'name': student.batches[0].name,
                'description': student.batches[0].description
            }
            student_data['batchId'] = student.batches[0].id
        
        # Add login credentials to response
        student_data['loginCredentials'] = {
            'username': phone,  # Parent phone number
            'password': unique_password,  # Unique generated password
            'note': 'Student logs in with Parent Phone Number + Unique Password'
        }
        
        return success_response('Student created successfully', student_data, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create student: {str(e)}', 500)

@students_bp.route('/<int:student_id>', methods=['PUT'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def update_student(student_id):
    """Update student information"""
    try:
        student = User.query.filter(
            User.id == student_id,
            User.role == UserRole.STUDENT
        ).first()
        
        if not student:
            return error_response('Student not found', 404)
        
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Update basic information
        if 'firstName' in data:
            student.first_name = data['firstName'].strip()
        if 'lastName' in data:
            student.last_name = data['lastName'].strip()
        if 'email' in data:
            if data['email']:
                # Check if email is already taken
                existing_email = User.query.filter(
                    User.email == data['email'],
                    User.id != student_id
                ).first()
                if existing_email:
                    return error_response('Email is already taken', 409)
            student.email = data['email'].strip() if data['email'] else None
        
        if 'studentId' in data:
            student.student_id = data['studentId'].strip() if data['studentId'] else None
        
        if 'phoneNumber' in data:
            phone = validate_phone(data['phoneNumber'])
            if not phone:
                return error_response('Invalid phone number format', 400)
            
            # Check if phone is already taken
            existing_phone = User.query.filter(
                User.phoneNumber == phone,
                User.id != student_id
            ).first()
            if existing_phone:
                return error_response('Phone number is already taken', 409)
            
            student.phoneNumber = phone
            student.phone = phone  # Sync phone field for SMS
            student.guardian_phone = phone  # Sync guardian phone for SMS
        
        if 'dateOfBirth' in data and data['dateOfBirth']:
            try:
                student.date_of_birth = datetime.strptime(data['dateOfBirth'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid date format. Use YYYY-MM-DD', 400)
        
        if 'address' in data:
            student.address = data['address'].strip() if data['address'] else None
        
        if 'school' in data:
            student.address = data['school'].strip() if data['school'] else None
        
        if 'guardianPhone' in data:
            guardian_phone = data['guardianPhone'].strip() if data['guardianPhone'] else None
            student.guardian_phone = guardian_phone
            # Sync phone fields to ensure SMS works
            if guardian_phone:
                student.phone = guardian_phone
                if not student.phoneNumber:  # Only update if phoneNumber is not set
                    student.phoneNumber = guardian_phone
        
        if 'guardianName' in data:
            student.guardian_name = data['guardianName'].strip() if data['guardianName'] else None
        
        if 'emergencyContact' in data:
            student.emergency_contact = data['emergencyContact'].strip() if data['emergencyContact'] else None
        
        if 'isActive' in data:
            student.is_active = data['isActive']
        
        # Update batch assignment
        if 'batchId' in data:
            student.batches.clear()
            if data['batchId']:
                batch = Batch.query.get(data['batchId'])
                if batch:
                    student.batches.append(batch)
        
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Prepare response data
        student_data = serialize_user(student)
        student_data['firstName'] = student_data.get('first_name', '')
        student_data['lastName'] = student_data.get('last_name', '')
        student_data['phoneNumber'] = student_data.get('phoneNumber', '')  # Fixed: use phoneNumber not phone
        student_data['studentId'] = student_data.get('student_id', '')
        student_data['isActive'] = student_data.get('is_active', True)
        student_data['guardianPhone'] = student_data.get('guardian_phone', '')
        student_data['guardianName'] = student_data.get('guardian_name', '')
        student_data['school'] = student_data.get('address', '')
        
        if student.batches:
            student_data['batch'] = {
                'id': student.batches[0].id,
                'name': student.batches[0].name,
                'description': student.batches[0].description
            }
            student_data['batchId'] = student.batches[0].id
        
        return success_response('Student updated successfully', student_data)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update student: {str(e)}', 500)

@students_bp.route('/<int:student_id>', methods=['DELETE'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def delete_student(student_id):
    """Delete a student (soft delete by deactivating)"""
    try:
        student = User.query.filter(
            User.id == student_id,
            User.role == UserRole.STUDENT
        ).first()
        
        if not student:
            return error_response('Student not found', 404)
        
        # Soft delete by deactivating
        student.is_active = False
        student.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return success_response('Student deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete student: {str(e)}', 500)

@students_bp.route('/<int:student_id>/reset-password', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def reset_student_password(student_id):
    """Reset student password to unique generated password"""
    try:
        student = User.query.filter(
            User.id == student_id,
            User.role == UserRole.STUDENT
        ).first()
        
        if not student:
            return error_response('Student not found', 404)
        
        # Generate new unique password based on student info
        from utils.password_generator import generate_simple_unique_password
        new_password = generate_simple_unique_password(student.first_name, student.guardian_phone)
        student.password_hash = generate_password_hash(new_password)
        student.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return success_response('Password reset successfully', {'newPassword': new_password})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to reset password: {str(e)}', 500)

@students_bp.route('/bulk-import', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def bulk_import_students():
    """Bulk import students from CSV data"""
    try:
        data = request.get_json()
        
        if not data or 'students' not in data:
            return error_response('Students data is required', 400)
        
        students_data = data['students']
        successful_imports = []
        failed_imports = []
        
        for idx, student_data in enumerate(students_data):
            try:
                # Validate required fields
                if not all(field in student_data for field in ['firstName', 'lastName', 'phoneNumber']):
                    failed_imports.append({
                        'row': idx + 1,
                        'error': 'Missing required fields (firstName, lastName, phoneNumber)',
                        'data': student_data
                    })
                    continue
                
                # Validate phone number
                phone = validate_phone(student_data['phoneNumber'])
                if not phone:
                    failed_imports.append({
                        'row': idx + 1,
                        'error': 'Invalid phone number format',
                        'data': student_data
                    })
                    continue
                
                # Check if student already exists
                existing_user = User.query.filter_by(phoneNumber=phone).first()
                if existing_user:
                    failed_imports.append({
                        'row': idx + 1,
                        'error': 'Student with this phone number already exists',
                        'data': student_data
                    })
                    continue
                
                # Generate student ID if not provided
                student_id = student_data.get('studentId')
                if not student_id:
                    current_year = datetime.now().year
                    count = User.query.filter(User.role == UserRole.STUDENT).count()
                    student_id = f"{current_year}{count + len(successful_imports) + 1:04d}"
                
                # Create new student
                student = User(
                    phoneNumber=phone,  # This will be guardian phone for login
                    first_name=student_data['firstName'].strip(),
                    last_name=student_data['lastName'].strip(),
                    email=student_data.get('email', '').strip() if student_data.get('email') else None,
                    role=UserRole.STUDENT,
                    is_active=True
                )
                
                # Generate unique password for student
                from utils.password_generator import generate_simple_unique_password
                unique_password = generate_simple_unique_password(student_data['firstName'].strip(), phone)
                student.password_hash = generate_password_hash(unique_password)
                
                db.session.add(student)
                db.session.flush()
                
                # Assign to batch if provided
                batch_id = student_data.get('batchId')
                if batch_id:
                    batch = Batch.query.get(batch_id)
                    if batch:
                        student.batches.append(batch)
                
                successful_imports.append({
                    'row': idx + 1,
                    'studentId': student_id,
                    'name': f"{student.first_name} {student.last_name}",
                    'phone': phone
                })
                
            except Exception as e:
                failed_imports.append({
                    'row': idx + 1,
                    'error': str(e),
                    'data': student_data
                })
        
        if successful_imports:
            db.session.commit()
        else:
            db.session.rollback()
        
        return success_response('Bulk import completed', {
            'successful': len(successful_imports),
            'failed': len(failed_imports),
            'successfulImports': successful_imports,
            'failedImports': failed_imports
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to import students: {str(e)}', 500)