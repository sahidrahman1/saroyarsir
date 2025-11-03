"""
Create default users in the database
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, User, UserRole
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    try:
        # Check if users already exist
        existing_teacher = User.query.filter_by(phoneNumber='01812345678').first()
        if existing_teacher:
            print('ℹ️  Users already exist in database')
        else:
            # Create teacher
            teacher = User(
                phoneNumber='01812345678',
                first_name='Sample',
                last_name='Teacher',
                role=UserRole.TEACHER,
                password_hash=generate_password_hash('teacher123'),
                is_active=True
            )
            db.session.add(teacher)
            
            # Create student
            student = User(
                phoneNumber='01912345678',
                first_name='Sample',
                last_name='Student',
                role=UserRole.STUDENT,
                password_hash=generate_password_hash('student123'),
                is_active=True
            )
            db.session.add(student)
            
            # Create admin
            admin = User(
                phoneNumber='01712345678',
                first_name='Admin',
                last_name='User',
                role=UserRole.SUPER_USER,
                password_hash=generate_password_hash('admin123'),
                is_active=True
            )
            db.session.add(admin)
            
            db.session.commit()
            print('✅ Default users created successfully!')
            print('   Teacher: 01812345678 / teacher123')
            print('   Student: 01912345678 / student123')
            print('   Admin: 01712345678 / admin123')
            
    except Exception as e:
        print(f'❌ Error creating users: {e}')
        import traceback
        traceback.print_exc()
