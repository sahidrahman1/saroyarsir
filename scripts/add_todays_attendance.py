#!/usr/bin/env python3
"""
Add today's attendance record
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

def add_todays_attendance():
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
            
            # Today's date
            today = date.today()  # 2025-10-11
            print(f'📅 Adding attendance for: {today}')
            
            for i, student in enumerate(students):
                # Check if attendance already exists for today
                existing = Attendance.query.filter_by(
                    user_id=student.id,
                    batch_id=hsc_batch.id,
                    date=today
                ).first()
                
                if existing:
                    print(f'   ⚠️  Attendance already exists for {student.full_name}')
                    continue
                
                # Make most students present, one absent, one late
                if i == 0:
                    status = AttendanceStatus.LATE
                elif i == 1:
                    status = AttendanceStatus.ABSENT
                else:
                    status = AttendanceStatus.PRESENT
                
                # Create attendance record
                attendance = Attendance(
                    user_id=student.id,
                    batch_id=hsc_batch.id,
                    date=today,
                    status=status,
                    marked_by=1,  # Assuming teacher ID 1
                    notes=f'Attendance for {today}'
                )
                
                db.session.add(attendance)
                print(f'✅ Added: {student.full_name} - {status.value}')
            
            # Commit changes
            db.session.commit()
            print(f'\n🎉 Successfully added today\'s attendance!')
            
            # Show count for today
            today_count = Attendance.query.filter_by(batch_id=hsc_batch.id, date=today).count()
            print(f'📊 Total attendance records for {today}: {today_count}')
            
        except Exception as e:
            print(f'❌ Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    add_todays_attendance()