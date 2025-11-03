"""
Simple test for student loading in marks entry
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, User, UserRole, Batch

app = create_app()

with app.app_context():
    print("🔍 Checking database for students and batches...")
    
    # Check batches
    batches = Batch.query.all()
    print(f"📚 Found {len(batches)} batches:")
    
    for batch in batches:
        students = [s for s in batch.students if s.is_active]
        print(f"  - {batch.name} (ID: {batch.id}) - {len(students)} students")
        
        if students:
            print("    Students:")
            for student in students[:3]:  # First 3 students
                print(f"      * {student.full_name} (ID: {student.id}, Phone: {student.phoneNumber})")
    
    # Check all students
    all_students = User.query.filter_by(role=UserRole.STUDENT, is_active=True).all()
    print(f"\n👥 Total active students: {len(all_students)}")
    
    # Check teachers
    teachers = User.query.filter_by(role=UserRole.TEACHER, is_active=True).all()
    print(f"👨‍🏫 Total teachers: {len(teachers)}")
    
    if teachers:
        teacher = teachers[0]
        print(f"    Teacher: {teacher.full_name} (Phone: {teacher.phoneNumber})")
    
    print("\n✅ Database check complete!")