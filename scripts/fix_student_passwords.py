"""
Fix student passwords - Generate random unique passwords for each student
"""
import os
import random
import string
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, User, UserRole
from werkzeug.security import generate_password_hash

def generate_random_password(length=8):
    """Generate a random password with letters, numbers and special characters"""
    # Mix of uppercase, lowercase, numbers and some special characters
    characters = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def generate_simple_random_password(length=6):
    """Generate a simple random password with only letters and numbers"""
    characters = string.ascii_lowercase + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

app = create_app()

with app.app_context():
    try:
        # Get all students
        students = User.query.filter_by(role=UserRole.STUDENT).all()
        
        if not students:
            print('❌ No students found in database')
            exit()
        
        print(f'🔐 Updating passwords for {len(students)} students...')
        print('=' * 60)
        
        updated_students = []
        
        for student in students:
            # Generate a new random password
            new_password = generate_simple_random_password(8)
            
            # Update the password hash
            student.password_hash = generate_password_hash(new_password)
            
            # Store for display
            updated_students.append({
                'phone': student.phoneNumber,
                'name': student.full_name,
                'password': new_password,
                'guardian_phone': student.guardian_phone or 'Not set'
            })
            
            print(f'✅ {student.full_name}')
            print(f'   📞 Phone: {student.phoneNumber}')
            print(f'   🔑 New Password: {new_password}')
            print(f'   👤 Guardian Phone: {student.guardian_phone or "Not set"}')
            print()
        
        # Commit all changes
        db.session.commit()
        
        print('=' * 60)
        print('🎉 All student passwords updated successfully!')
        print()
        print('📋 STUDENT LOGIN CREDENTIALS:')
        print('=' * 60)
        
        for student in updated_students:
            print(f'👤 {student["name"]}')
            print(f'   📞 Login Phone: {student["phone"]}')
            print(f'   🔑 Password: {student["password"]}')
            print(f'   👨‍👩‍👧‍👦 Guardian: {student["guardian_phone"]}')
            print()
        
        print('=' * 60)
        print('💡 IMPORTANT NOTES:')
        print('• Students login with their OWN phone number + new random password')
        print('• Each student now has a unique random password')
        print('• Guardian phone is set for reference only')
        print('• Save these credentials as they are randomly generated!')
        
    except Exception as e:
        db.session.rollback()
        print(f'❌ Error updating student passwords: {e}')
        import traceback
        traceback.print_exc()