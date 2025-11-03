#!/usr/bin/env python3
"""
Create test attendance records for monthly view testing
"""
import os
from datetime import datetime, date

# Set MySQL environment variables
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, Attendance, User, Batch, AttendanceStatus, UserRole

def create_test_attendance():
    app = create_app()
    with app.app_context():
        try:
            # Find HSC Mathematics Batch A
            hsc_batch = Batch.query.filter_by(name='HSC Mathematics Batch A').first()
            if not hsc_batch:
                print('❌ HSC Mathematics Batch A not found')
                return
            
            print(f'📚 Found batch: {hsc_batch.name} (ID: {hsc_batch.id})')
            
            # Get students in the batch
            students = hsc_batch.students
            print(f'👥 Students in batch: {len(students)}')
            
            if not students:
                print('❌ No students in batch')
                return
            
            # Create attendance records for October 2025 (current month)
            year = 2025
            month = 10
            
            # Create attendance for first 10 days of October
            for day in range(1, 11):
                attendance_date = date(year, month, day)
                
                for i, student in enumerate(students):
                    # Check if attendance already exists
                    existing = Attendance.query.filter_by(
                        user_id=student.id,
                        batch_id=hsc_batch.id,
                        date=attendance_date
                    ).first()
                    
                    if existing:
                        continue  # Skip if already exists
                    
                    # Vary the attendance (some present, some absent)
                    if day <= 5:
                        # First 5 days - all present
                        status = AttendanceStatus.PRESENT
                    elif day <= 8:
                        # Days 6-8 - alternate present/absent
                        status = AttendanceStatus.PRESENT if i % 2 == 0 else AttendanceStatus.ABSENT
                    else:
                        # Days 9-10 - mostly present with some late
                        if i == 0:
                            status = AttendanceStatus.LATE
                        else:
                            status = AttendanceStatus.PRESENT
                    
                    # Create attendance record
                    attendance = Attendance(
                        user_id=student.id,
                        batch_id=hsc_batch.id,
                        date=attendance_date,
                        status=status,
                        marked_by=1,  # Assuming teacher ID 1
                        notes=f'Test attendance for {attendance_date}'
                    )
                    
                    db.session.add(attendance)
                    print(f'✅ Created attendance: {student.full_name} - {attendance_date} - {status.value}')
            
            # Commit all changes
            db.session.commit()
            print(f'\n🎉 Successfully created test attendance records for October 2025')
            
            # Show summary
            total_records = Attendance.query.filter_by(batch_id=hsc_batch.id).count()
            print(f'📊 Total attendance records for batch: {total_records}')
            
        except Exception as e:
            print(f'❌ Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    create_test_attendance()