#!/usr/bin/env python3
"""
Fix Monthly Exams Script
Recalculates total marks for existing monthly exams based on individual exams
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, MonthlyExam, IndividualExam
from sqlalchemy import func

def fix_monthly_exam_totals():
    """Fix total marks for all monthly exams"""
    app = create_app()
    
    with app.app_context():
        print("🔧 FIXING MONTHLY EXAM TOTALS")
        print("=" * 50)
        
        # Get all monthly exams
        monthly_exams = MonthlyExam.query.all()
        
        if not monthly_exams:
            print("ℹ️  No monthly exams found.")
            return
        
        fixed_count = 0
        
        for exam in monthly_exams:
            print(f"\n📝 Processing: {exam.title} ({exam.month}/{exam.year}) - Batch: {exam.batch.name}")
            print(f"   Current Total: {exam.total_marks}")
            
            # Calculate actual total from individual exams
            actual_total = db.session.query(func.sum(IndividualExam.marks)).filter_by(monthly_exam_id=exam.id).scalar() or 0
            
            print(f"   Calculated Total: {actual_total}")
            
            if exam.total_marks != actual_total:
                # Update the monthly exam
                old_total = exam.total_marks
                exam.total_marks = actual_total
                exam.pass_marks = int(actual_total * 0.33) if actual_total > 0 else 0
                
                print(f"   ✅ FIXED: {old_total} → {actual_total} (Pass: {exam.pass_marks})")
                fixed_count += 1
            else:
                print(f"   ✓ Already correct")
        
        if fixed_count > 0:
            try:
                db.session.commit()
                print(f"\n🎉 SUCCESS: Fixed {fixed_count} monthly exams!")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ ERROR: Failed to save changes: {e}")
        else:
            print(f"\n✅ All monthly exams already have correct totals!")

if __name__ == '__main__':
    fix_monthly_exam_totals()