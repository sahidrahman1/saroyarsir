"""
Create test data for batches and students
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, User, UserRole, Batch
from werkzeug.security import generate_password_hash
from datetime import date
from decimal import Decimal

app = create_app()

with app.app_context():
    try:
        # Create sample batches if they don't exist
        existing_batch = Batch.query.filter_by(name='Class 10 Mathematics').first()
        if not existing_batch:
            # Create batch
            batch = Batch(
                name='Class 10 Mathematics',
                subject='Mathematics',
                start_date=date.today(),
                description='Class 10 - Mathematics',
                status='active',
                is_active=True,
                fee_amount=Decimal('2000.00'),
                max_students=30
            )
            db.session.add(batch)
            db.session.flush()  # To get the batch ID
            
            print('✅ Created batch: Class 10 Mathematics')
        else:
            batch = existing_batch
            print('ℹ️  Batch already exists: Class 10 Mathematics')
        
        # Create sample students if they don't exist
        student_data = [
            {'phone': '01901234567', 'name': 'রহিম', 'last': 'আহমেদ'},
            {'phone': '01901234568', 'name': 'করিম', 'last': 'হাসান'},
            {'phone': '01901234569', 'name': 'ফাতেমা', 'last': 'খাতুন'},
            {'phone': '01901234570', 'name': 'আয়েশা', 'last': 'বেগম'},
            {'phone': '01901234571', 'name': 'মোহাম্মদ', 'last': 'আলী'},
        ]
        
        students_created = 0
        for student_info in student_data:
            existing_student = User.query.filter_by(phoneNumber=student_info['phone']).first()
            if not existing_student:
                # Create student
                student = User(
                    phoneNumber=student_info['phone'],
                    first_name=student_info['name'],
                    last_name=student_info['last'],
                    role=UserRole.STUDENT,
                    password_hash=generate_password_hash('student123'),
                    is_active=True,
                    guardian_phone='01812345678'  # Teacher's phone as guardian
                )
                db.session.add(student)
                db.session.flush()
                
                # Add student to batch
                student.batches.append(batch)
                students_created += 1
                print(f'✅ Created student: {student_info["name"]} {student_info["last"]} ({student_info["phone"]})')
            else:
                # Add existing student to batch if not already added
                if batch not in existing_student.batches:
                    existing_student.batches.append(batch)
                    print(f'ℹ️  Added existing student to batch: {existing_student.full_name}')
        
        db.session.commit()
        
        # Print summary
        total_students = len([s for s in batch.students if s.is_active])
        print(f'\n🎉 Test data creation completed!')
        print(f'📚 Batch: {batch.name}')
        print(f'👥 Total students in batch: {total_students}')
        print(f'🆕 Students created: {students_created}')
        print(f'\n🔐 All students can login with password: student123')
        print(f'📞 Guardian phone for all students: 01812345678')
        
    except Exception as e:
        db.session.rollback()
        print(f'❌ Error creating test data: {e}')
        import traceback
        traceback.print_exc()