"""
Create test data for monthly exams
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, User, UserRole, Batch, MonthlyExam, IndividualExam, MonthlyMark, Attendance, AttendanceStatus
from datetime import datetime, date, timedelta
import random

app = create_app()

with app.app_context():
    try:
        # Get or create a batch
        batch = Batch.query.first()
        if not batch:
            batch = Batch(
                name="Test Batch",
                subject="Mathematics",
                class_level="HSC",
                is_active=True
            )
            db.session.add(batch)
            db.session.flush()
        
        # Get or create teacher
        teacher = User.query.filter_by(role=UserRole.TEACHER).first()
        if not teacher:
            print("No teacher found, please run create_default_users.py first")
            exit(1)
        
        # Get or create students
        students = User.query.filter_by(role=UserRole.STUDENT).limit(5).all()
        if len(students) < 3:
            # Create some students
            for i in range(3):
                student = User(
                    phoneNumber=f'01{900000000 + i}',
                    first_name=f'Student{i+1}',
                    last_name='Test',
                    role=UserRole.STUDENT,
                    password_hash='dummy_hash',
                    is_active=True
                )
                db.session.add(student)
                students.append(student)
            db.session.flush()
            
        # Associate students with batch
        for student in students[:3]:
            if batch not in student.batches:
                student.batches.append(batch)
        
        # Create or get monthly exam
        monthly_exam = MonthlyExam.query.first()
        if not monthly_exam:
            monthly_exam = MonthlyExam(
                title="Test Monthly Exam",
                month=datetime.now().month,
                year=datetime.now().year,
                batch_id=batch.id,
                teacher_id=teacher.id,
                is_active=True
            )
            db.session.add(monthly_exam)
            db.session.flush()
        
        # Create individual exams
        subjects = ['Math', 'Physics', 'Chemistry']
        individual_exams = IndividualExam.query.filter_by(monthly_exam_id=monthly_exam.id).all()
        
        if len(individual_exams) < 3:
            for i, subject in enumerate(subjects):
                exam = IndividualExam(
                    title=f"{subject} Test",
                    subject=subject,
                    marks=100,
                    monthly_exam_id=monthly_exam.id,
                    order_index=i
                )
                db.session.add(exam)
                individual_exams.append(exam)
            db.session.flush()
        
        # Create marks for each student
        for student in students[:3]:
            for exam in individual_exams[:3]:
                existing_mark = MonthlyMark.query.filter_by(
                    user_id=student.id,
                    individual_exam_id=exam.id
                ).first()
                
                if not existing_mark:
                    marks_obtained = random.randint(60, 95)
                    mark = MonthlyMark(
                        monthly_exam_id=monthly_exam.id,
                        user_id=student.id,
                        individual_exam_id=exam.id,
                        marks_obtained=marks_obtained,
                        total_marks=exam.marks,
                        percentage=(marks_obtained / exam.marks) * 100,
                        is_absent=False
                    )
                    db.session.add(mark)
        
        # Create attendance records
        for student in students[:3]:
            # Create attendance for the past 30 days
            for day_offset in range(30):
                attendance_date = date.today() - timedelta(days=day_offset)
                
                existing_attendance = Attendance.query.filter_by(
                    user_id=student.id,
                    date=attendance_date,
                    batch_id=batch.id
                ).first()
                
                if not existing_attendance:
                    attendance = Attendance(
                        user_id=student.id,
                        batch_id=batch.id,
                        date=attendance_date,
                        status=AttendanceStatus.PRESENT if random.random() > 0.2 else AttendanceStatus.ABSENT
                    )
                    db.session.add(attendance)
        
        db.session.commit()
        print("✅ Test monthly exam data created successfully!")
        print(f"   Monthly Exam: {monthly_exam.title}")
        print(f"   Individual Exams: {len(individual_exams)}")
        print(f"   Students: {len(students[:3])}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()