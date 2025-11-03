#!/usr/bin/env python3
"""
Fix SMS template for exam results
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import SmsTemplate, User, UserRole, db

def main():
    app = create_app()
    with app.app_context():
        # Check if there are any exam templates
        existing_templates = SmsTemplate.query.filter_by(category='exam').all()
        print(f"Found {len(existing_templates)} existing exam templates:")
        for t in existing_templates:
            print(f"  - {t.name}: {t.content}")
        
        # Get a super user to create the template
        super_user = User.query.filter_by(role=UserRole.SUPER_USER).first()
        if not super_user:
            super_user = User.query.filter_by(role=UserRole.TEACHER).first()
        
        if not super_user:
            print("No super user or teacher found to create template")
            return
        
        # Create a proper exam result template if it doesn't exist
        exam_template = SmsTemplate.query.filter_by(
            category='exam',
            name='Exam Result Notification'
        ).first()
        
        if not exam_template:
            print("Creating new exam result template...")
            exam_template = SmsTemplate(
                name='Exam Result Notification',
                subject='Exam Result',
                content='প্রিয় অভিভাবক, আপনার সন্তান {student_name} এর {subject} ({exam_title}) এ নম্বর: {marks_obtained}/{total_marks} ({percentage}) - গ্রেড: {grade}। GS Student Nursing Center',
                variables=['student_name', 'subject', 'exam_title', 'marks_obtained', 'total_marks', 'percentage', 'grade'],
                category='exam',
                is_active=True,
                created_by=super_user.id
            )
            db.session.add(exam_template)
            db.session.commit()
            print(f"Created template: {exam_template.name}")
        else:
            print(f"Template already exists: {exam_template.name}")
            print(f"Content: {exam_template.content}")

if __name__ == '__main__':
    main()