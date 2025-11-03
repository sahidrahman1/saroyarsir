#!/usr/bin/env python3
"""
Test batch students enrollment
"""
import os

# Set MySQL environment variables
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import User, Batch, UserRole

def test_batch_students():
    app = create_app()
    with app.app_context():
        try:
            # Get all batches
            batches = Batch.query.all()
            print(f'📚 Found {len(batches)} batches:')
            
            for batch in batches:
                print(f'\n   Batch: {batch.name}')
                print(f'   ID: {batch.id}')
                print(f'   Description: {batch.description}')
                print(f'   Students enrolled: {len(batch.students)}')
                
                if batch.students:
                    for student in batch.students:
                        print(f'     - {student.full_name} (ID: {student.id})')
                else:
                    print('     - No students enrolled')
            
            # Get all students
            students = User.query.filter_by(role=UserRole.STUDENT, is_active=True).all()
            print(f'\n👥 Found {len(students)} active students:')
            
            for student in students[:5]:  # Show first 5
                print(f'   - {student.full_name} (ID: {student.id})')
                
        except Exception as e:
            print(f'Error: {e}')

if __name__ == '__main__':
    test_batch_students()