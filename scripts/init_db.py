#!/usr/bin/env python3
"""
Database initialization script for SmartGardenHub
Creates tables and initial data
"""
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import *
from config import Config
import bcrypt

def init_database():
    """Initialize the database with tables and initial data"""
    print("🚀 Initializing SmartGardenHub Database...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables (be careful in production!)
            print("🗑️  Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("🔨 Creating database tables...")
            db.create_all()
            
            # Create initial super user
            print("👤 Creating initial super user...")
            
            # Hash the default password
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            super_user = User(
                first_name="System",
                last_name="Administrator",
                phoneNumber="01712345678",
                email="admin@smartgardenhub.com",
                password_hash=password_hash,
                role=UserRole.SUPER_USER,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(super_user)
            
            # Create sample teacher
            print("👨‍🏫 Creating sample teacher...")
            teacher_password_hash = bcrypt.hashpw('teacher123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            teacher = User(
                first_name="Sample",
                last_name="Teacher",
                phoneNumber="01812345678",
                email="teacher@smartgardenhub.com",
                password_hash=teacher_password_hash,
                role=UserRole.TEACHER,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(teacher)
            
            # Create sample student
            print("👨‍🎓 Creating sample student...")
            student_password_hash = bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            student = User(
                first_name="Sample",
                last_name="Student",
                phoneNumber="01912345678",
                email="student@smartgardenhub.com",
                password_hash=student_password_hash,
                role=UserRole.STUDENT,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(student)
            
            # Create sample batch
            print("📚 Creating sample batch...")
            batch = Batch(
                name="Class 10 - Science",
                description="Class 10 Science batch for HSC preparation",
                start_date=datetime.now().date(),
                fee_amount=2000.0,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(batch)
            db.session.flush()  # Get the batch ID
            
            # Enroll student in batch
            print("🎒 Enrolling student in batch...")
            # Use the many-to-many relationship
            batch.students.append(student)
            
            # Create sample exam
            print("📝 Creating sample exam...")
            exam = Exam(
                title="Sample Science Quiz",
                description="Basic science questions for Class 10",
                exam_type=ExamType.ONLINE,
                duration=30,  # 30 minutes
                total_marks=20,
                pass_marks=12,
                instructions="Read all questions carefully. Select the best answer for each question.",
                status=ExamStatus.ACTIVE,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow().replace(hour=23, minute=59),
                created_by=teacher.id,
                created_at=datetime.utcnow()
            )
            
            db.session.add(exam)
            db.session.flush()  # Get the exam ID
            
            # Create sample questions
            print("❓ Creating sample questions...")
            
            questions_data = [
                {
                    "question": "What is the chemical symbol for water?",
                    "options": ["H2O", "CO2", "NaCl", "O2"],
                    "correct_answer": 0,
                    "marks": 2
                },
                {
                    "question": "Which planet is known as the Red Planet?",
                    "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                    "correct_answer": 1,
                    "marks": 2
                },
                {
                    "question": "What is the process by which plants make their food?",
                    "options": ["Respiration", "Digestion", "Photosynthesis", "Transpiration"],
                    "correct_answer": 2,
                    "marks": 2
                },
                {
                    "question": "What is the hardest natural substance on Earth?",
                    "options": ["Gold", "Iron", "Diamond", "Silver"],
                    "correct_answer": 2,
                    "marks": 2
                },
                {
                    "question": "Which gas makes up about 78% of Earth's atmosphere?",
                    "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
                    "correct_answer": 2,
                    "marks": 2
                }
            ]
            
            for i, q_data in enumerate(questions_data):
                question = Question(
                    exam_id=exam.id,
                    question_text=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    marks=q_data["marks"],
                    order_index=i + 1,
                    created_at=datetime.utcnow()
                )
                db.session.add(question)
            
            # Create sample fee record
            print("💰 Creating sample fee record...")
            fee = Fee(
                user_id=student.id,
                batch_id=batch.id,
                amount=2000.0,
                due_date=datetime.utcnow().replace(day=10).date(),
                status=FeeStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            db.session.add(fee)
            
            # Commit all changes
            print("💾 Saving changes to database...")
            db.session.commit()
            
            print("\n✅ Database initialization completed successfully!")
            print("\n🔑 Login Credentials:")
            print("=" * 50)
            print("Super User:")
            print("  Phone: 01712345678")
            print("  Password: admin123")
            print("\nTeacher:")
            print("  Phone: 01812345678")
            print("  Password: teacher123")
            print("\nStudent:")
            print("  Phone: 01912345678")
            print("  Password: student123")
            print("=" * 50)
            print("\n🌐 You can now start the application with: python app.py")
            
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    if init_database():
        print("\n🎉 Setup completed! Your SmartGardenHub is ready to use.")
    else:
        print("\n💥 Setup failed! Please check the error messages above.")
        sys.exit(1)