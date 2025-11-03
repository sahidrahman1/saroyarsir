#!/usr/bin/env python3
"""
Add students to HSC Mathematics Batch A for testing
"""
import os

# Set MySQL environment variables
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, User, Batch, UserRole

def add_students_to_hsc_batch():
    app = create_app()
    with app.app_context():
        try:
            # Find HSC Mathematics Batch A
            hsc_batch = Batch.query.filter_by(name='HSC Mathematics Batch A').first()
            if not hsc_batch:
                print('❌ HSC Mathematics Batch A not found')
                return
            
            print(f'📚 Found batch: {hsc_batch.name} (ID: {hsc_batch.id})')
            print(f'   Current students: {len(hsc_batch.students)}')
            
            # Get some available students (that are not already enrolled)
            available_students = User.query.filter_by(
                role=UserRole.STUDENT, 
                is_active=True
            ).all()
            
            # Filter out students already in this batch
            students_to_add = []
            for student in available_students:
                if hsc_batch not in student.batches:
                    students_to_add.append(student)
                    if len(students_to_add) >= 5:  # Add up to 5 students
                        break
            
            if not students_to_add:
                print('❌ No available students to add')
                return
            
            print(f'\n👥 Adding {len(students_to_add)} students:')
            
            # Add students to batch
            for student in students_to_add:
                hsc_batch.students.append(student)
                print(f'   ✅ Added: {student.full_name} (ID: {student.id})')
            
            # Commit changes
            db.session.commit()
            
            print(f'\n🎉 Successfully added students to {hsc_batch.name}')
            print(f'   Total students now: {len(hsc_batch.students)}')
            
        except Exception as e:
            print(f'❌ Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    add_students_to_hsc_batch()