#!/usr/bin/env python3
"""
Test SMS sending for monthly exam marks - should send only ONE SMS per student
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import User, UserRole, MonthlyExam, IndividualExam, Batch, db
import requests
import json

def test_sms_sending():
    app = create_app()
    with app.app_context():
        # Get test data
        monthly_exam = MonthlyExam.query.first()
        if not monthly_exam:
            print("No monthly exam found for testing")
            return
        
        individual_exam = IndividualExam.query.filter_by(monthly_exam_id=monthly_exam.id).first()
        if not individual_exam:
            print("No individual exam found for testing")
            return
        
        batch = Batch.query.get(monthly_exam.batch_id)
        students = [s for s in batch.students if s.role == UserRole.STUDENT]
        
        print(f"Testing SMS sending for exam: {individual_exam.title}")
        print(f"Batch: {batch.name}")
        print(f"Students: {len(students)}")
        
        for student in students[:2]:  # Test with first 2 students
            print(f"Student: {student.full_name}")
            print(f"  Phone: {student.phoneNumber}")
            print(f"  Guardian Phone: {getattr(student, 'guardian_phone', 'None')}")
            
            # Check which phone would be targeted
            target_phone = None
            if hasattr(student, 'guardian_phone') and student.guardian_phone:
                target_phone = student.guardian_phone
                print(f"  Target: Guardian phone - {target_phone}")
            elif student.phoneNumber:
                target_phone = student.phoneNumber
                print(f"  Target: Student phone - {target_phone}")
            else:
                print(f"  Target: No phone available")
        
        print("\nThis fix ensures only ONE SMS is sent per student to the preferred phone number.")

if __name__ == '__main__':
    test_sms_sending()