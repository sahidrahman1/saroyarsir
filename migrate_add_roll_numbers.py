#!/usr/bin/env python3
"""
Database migration to add roll_number and previous_position columns to MonthlyRanking table
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, MonthlyRanking
from sqlalchemy import text

def migrate_add_roll_numbers():
    """Add roll_number and previous_position columns to monthly_rankings table"""
    try:
        app = create_app()
        
        with app.app_context():
            print("Starting migration: Add roll numbers and previous position to MonthlyRanking...")
            
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('monthly_rankings')]
            
            migrations_needed = []
            
            if 'roll_number' not in existing_columns:
                migrations_needed.append("ADD COLUMN roll_number INTEGER")
                print("- Will add roll_number column")
            else:
                print("- roll_number column already exists")
            
            if 'previous_position' not in existing_columns:
                migrations_needed.append("ADD COLUMN previous_position INTEGER")
                print("- Will add previous_position column")
            else:
                print("- previous_position column already exists")
            
            if not migrations_needed:
                print("✅ All columns already exist. Migration not needed.")
                return True
            
            # Execute migrations
            for migration in migrations_needed:
                sql = f"ALTER TABLE monthly_rankings {migration}"
                print(f"Executing: {sql}")
                db.session.execute(text(sql))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            
            # Verify the changes
            inspector = db.inspect(db.engine)
            updated_columns = [col['name'] for col in inspector.get_columns('monthly_rankings')]
            
            print("\nUpdated table schema:")
            for col in inspector.get_columns('monthly_rankings'):
                print(f"  - {col['name']}: {col['type']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        try:
            db.session.rollback()
        except:
            pass
        return False

def create_sample_monthly_exam_data():
    """Create sample data for testing if none exists"""
    try:
        app = create_app()
        
        with app.app_context():
            from models import MonthlyExam, IndividualExam, User, Batch, UserRole
            
            # Check if we have any monthly exams
            exam_count = MonthlyExam.query.count()
            if exam_count > 0:
                print(f"✅ Found {exam_count} existing monthly exams")
                return True
            
            print("Creating sample monthly exam data...")
            
            # Get first active batch
            batch = Batch.query.filter_by(is_active=True).first()
            if not batch:
                print("❌ No active batch found. Cannot create sample data.")
                return False
            
            # Get a teacher to create the exam
            teacher = User.query.filter_by(role=UserRole.TEACHER, is_active=True).first()
            if not teacher:
                teacher = User.query.filter_by(role=UserRole.SUPER_USER, is_active=True).first()
            
            if not teacher:
                print("❌ No teacher found. Cannot create sample data.")
                return False
            
            # Create a monthly exam
            monthly_exam = MonthlyExam(
                title="Sample Monthly Exam - October 2025",
                description="Sample monthly exam for testing enhanced results",
                month=10,
                year=2025,
                total_marks=300,
                pass_marks=120,
                start_date=datetime(2025, 10, 1),
                end_date=datetime(2025, 10, 31),
                batch_id=batch.id,
                status='active',
                created_by=teacher.id
            )
            
            db.session.add(monthly_exam)
            db.session.flush()  # Get the ID
            
            # Create individual exams
            subjects = [
                ('Mathematics', 100),
                ('Physics', 100),
                ('Chemistry', 100)
            ]
            
            for i, (subject, marks) in enumerate(subjects):
                individual_exam = IndividualExam(
                    monthly_exam_id=monthly_exam.id,
                    title=f"{subject} Monthly Test",
                    subject=subject,
                    marks=marks,
                    exam_date=datetime(2025, 10, 5 + i * 2),
                    duration=120,
                    order_index=i
                )
                db.session.add(individual_exam)
            
            db.session.commit()
            print(f"✅ Created sample monthly exam: {monthly_exam.title}")
            print(f"   - Batch: {batch.name}")
            print(f"   - Individual exams: {len(subjects)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        try:
            db.session.rollback()
        except:
            pass
        return False

if __name__ == '__main__':
    print("🚀 Starting MonthlyRanking table migration...")
    print("=" * 50)
    
    success = migrate_add_roll_numbers()
    
    if success:
        print("\n📊 Creating sample data if needed...")
        create_sample_monthly_exam_data()
        
        print("\n" + "=" * 50)
        print("✅ Migration completed successfully!")
        print("\nEnhancements added:")
        print("- Roll number field for student identification")
        print("- Previous position tracking for ranking comparison")
        print("- Enhanced comprehensive results table")
        print("- Attendance marks calculation (1 mark per present day)")
        print("- Individual exam marks display with grades")
        print("- Position change tracking (up/down arrows)")
        print("- Teacher tools for roll number assignment")
        
        print("\n🎯 Next steps:")
        print("1. Restart the Flask server")
        print("2. Go to Monthly Exams → Results & Rankings")
        print("3. Click 'Comprehensive Results' to see the enhanced table")
        print("4. Use 'Assign Roll Numbers' or 'Auto-Assign by Rank' buttons")
    else:
        print("\n❌ Migration failed! Please check the error messages above.")
        sys.exit(1)