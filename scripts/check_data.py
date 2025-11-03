#!/usr/bin/env python3
"""
Check data storage in SmartGardenHub MySQL database
"""
import os
import sys

# Set MySQL environment variables
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import User, Batch, UserRole

def check_data_storage():
    print('📊 SMARTGARDENHUB DATA STORAGE REPORT')
    print('=' * 60)
    print()
    
    # Database connection info
    print('🗄️  DATABASE INFORMATION:')
    print('   Type: MySQL Server')
    print('   Host: localhost:3306')
    print('   Database: smartgardenhub')
    print('   User: root')
    print('   Connection: mysql+pymysql://root:***@localhost:3306/smartgardenhub')
    print()
    
    app = create_app()
    with app.app_context():
        try:
            # Check users
            users = User.query.all()
            print(f'👥 USERS DATA ({len(users)} total):')
            
            # Group by role
            teachers = [u for u in users if u.role == UserRole.TEACHER]
            students = [u for u in users if u.role == UserRole.STUDENT]
            admins = [u for u in users if u.role == UserRole.SUPER_USER]
            
            print(f'   • Teachers: {len(teachers)}')
            print(f'   • Students: {len(students)}')
            print(f'   • Super Users: {len(admins)}')
            print()
            
            # Show some user details
            if users:
                print('📋 SAMPLE USER DATA:')
                for user in users[:5]:  # Show first 5 users
                    print(f'   • {user.first_name} {user.last_name}')
                    print(f'     Role: {user.role.value}')
                    print(f'     Phone: {user.phoneNumber}')
                    if user.role == UserRole.STUDENT and user.guardian_name:
                        print(f'     Parent: {user.guardian_name} ({user.guardian_phone or "No phone"})')
                    print()
            
            # Check batches
            batches = Batch.query.all()
            print(f'📚 BATCHES DATA ({len(batches)} total):')
            for batch in batches:
                student_count = len([u for u in batch.users if u.role == UserRole.STUDENT])
                print(f'   • {batch.name}: {student_count} students')
            print()
            
            # Storage location
            print('💾 PHYSICAL DATA STORAGE:')
            print('   Location: MySQL Server Data Directory')
            print('   Default Path: C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Data\\smartgardenhub\\')
            print('   Tables: users, batches, sms_templates, sms_logs, etc.')
            print()
            
            print('✅ Database connection successful!')
            print('🔗 Access your data at: http://127.0.0.1:5001')
            
        except Exception as e:
            print(f'❌ Error connecting to database: {e}')
            print('Make sure MySQL server is running and credentials are correct.')

if __name__ == '__main__':
    check_data_storage()