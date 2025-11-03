"""Check 'f - Class' batch data"""
from app import create_app
from models import db, Batch, User, UserRole, Attendance
from datetime import datetime

app = create_app()

with app.app_context():
    # Find the batch
    batch = Batch.query.filter_by(name='f - Class').first()
    
    if not batch:
        print("❌ 'f - Class' batch NOT FOUND")
        print("\nAvailable batches:")
        all_batches = Batch.query.all()
        for b in all_batches:
            print(f"  - {b.name} (ID: {b.id})")
    else:
        print(f"✅ Batch found: {batch.name}")
        print(f"   ID: {batch.id}")
        print(f"   Code: {batch.code}")
        print(f"   Active: {batch.is_active}")
        
        # Get students
        students = User.query.join(User.batches).filter(
            User.role == UserRole.STUDENT,
            User.is_active == True,
            Batch.id == batch.id
        ).all()
        
        print(f"\n👥 Students enrolled: {len(students)}")
        if students:
            for student in students:
                print(f"   - {student.full_name} (ID: {student.id})")
        else:
            print("   ⚠️ NO STUDENTS ENROLLED")
        
        # Check attendance for October 2025
        month = 10
        year = 2025
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, 31).date()
        
        attendance_count = Attendance.query.filter(
            Attendance.batch_id == batch.id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).count()
        
        print(f"\n📅 Attendance records for October 2025: {attendance_count}")
