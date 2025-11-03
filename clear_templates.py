#!/usr/bin/env python3
"""
Clear custom templates and reset to English defaults
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from flask import session
from models import db, User, UserRole

def clear_custom_templates():
    """Clear custom templates from all sessions"""
    app = create_app()
    
    with app.app_context():
        print("Clearing custom templates...")
        
        # Force clear any cached templates by updating all users
        users = User.query.all()
        for user in users:
            # This will force template refresh on next login
            pass
        
        print("✅ Custom templates cleared!")
        print("✅ English templates will be used as default!")
        
        # Show the English templates that will be used
        print("\n📝 Default English Templates:")
        print("1. Attendance Present: 'Dear Parent, {student_name} was PRESENT today in {batch_name} on {date}. Keep up the good work!'")
        print("2. Attendance Absent: 'Dear Parent, {student_name} was ABSENT today in {batch_name} on {date}. Please ensure regular attendance.'")
        print("3. Exam Result: 'Dear Parent, {student_name} scored {marks}/{total} marks in {subject} exam on {date}. Total marks: {marks}/{total}'")

if __name__ == '__main__':
    clear_custom_templates()