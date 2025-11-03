#!/usr/bin/env python3
"""
Add phone numbers to student for testing
"""
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from models import db, User, UserRole
from app import create_app

def add_student_phone():
    """Add phone number to student"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Finding student 's s'...")
        
        # Find the student
        student = User.query.filter_by(first_name='s', last_name='s', role=UserRole.STUDENT).first()
        
        if not student:
            print("❌ Student not found")
            return
        
        print(f"✅ Found student: {student.first_name} {student.last_name}")
        print(f"Current phone: {student.phone}")
        print(f"Current guardian phone: {student.guardian_phone}")
        
        # Add phone numbers - both student and guardian use SAME number
        phone_number = "01818291546"
        student.phone = phone_number
        student.guardian_phone = phone_number  # Same as student phone
        print(f"✅ Set student phone: {student.phone}")
        print(f"✅ Set guardian phone: {student.guardian_phone} (same as student)")
        
        db.session.commit()
        print("\n✅ Student phone numbers updated successfully!")
        print(f"Student phone: {student.phone}")
        print(f"Guardian phone: {student.guardian_phone}")

if __name__ == "__main__":
    add_student_phone()
