"""
Fix monthly exam data with proper title and ensure comprehensive results work
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, MonthlyExam

app = create_app()

with app.app_context():
    try:
        # Update the monthly exam with a proper title
        monthly_exam = MonthlyExam.query.first()
        if monthly_exam:
            monthly_exam.title = "October 2025 Monthly Exam"
            db.session.commit()
            print(f"✅ Updated monthly exam title: {monthly_exam.title}")
        else:
            print("❌ No monthly exam found")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating monthly exam: {e}")
        import traceback
        traceback.print_exc()