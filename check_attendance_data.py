#!/usr/bin/env python3
"""
Check attendance data in database
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

def check_attendance_data():
    app = create_app()
    with app.app_context():
        try:
            # Get all attendance records
            attendance_records = Attendance.query.all()
            print(f'📊 Total attendance records: {len(attendance_records)}')
            
            if attendance_records:
                print('\n📋 Recent attendance records:')
                # Show most recent 10 records
                recent_records = Attendance.query.order_by(Attendance.created_at.desc()).limit(10).all()
                
                for record in recent_records:
                    user = User.query.get(record.user_id)
                    batch = Batch.query.get(record.batch_id)
                    
                    print(f'   • {user.full_name if user else "Unknown"} - {batch.name if batch else "Unknown"} - {record.date} - {record.status.value}')
            
            # Check by batch
            hsc_batch = Batch.query.filter_by(name='HSC Mathematics Batch A').first()
            if hsc_batch:
                batch_attendance = Attendance.query.filter_by(batch_id=hsc_batch.id).all()
                print(f'\n📚 HSC Mathematics Batch A attendance records: {len(batch_attendance)}')
                
                if batch_attendance:
                    # Group by date
                    dates = {}
                    for record in batch_attendance:
                        date_str = record.date.strftime('%Y-%m-%d')
                        if date_str not in dates:
                            dates[date_str] = []
                        dates[date_str].append(record)
                    
                    print('   Attendance by date:')
                    for date_str, records in sorted(dates.items()):
                        print(f'     {date_str}: {len(records)} students')
                        for record in records:
                            user = User.query.get(record.user_id)
                            print(f'       - {user.full_name if user else "Unknown"}: {record.status.value}')
            
        except Exception as e:
            print(f'❌ Error: {e}')

if __name__ == '__main__':
    check_attendance_data()