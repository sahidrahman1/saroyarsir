#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import User, UserRole, db
from werkzeug.security import generate_password_hash

def add_teacher():
    app = create_app()
    with app.app_context():
        try:
            # Check if teacher already exists
            existing_user = User.query.filter_by(phoneNumber='01762602056').first()
            if existing_user:
                print(f"❌ User with phone number 01762602056 already exists!")
                print(f"   Name: {existing_user.full_name}")
                print(f"   Role: {existing_user.role.value}")
                return False

            # Create new teacher
            teacher = User(
                phoneNumber='01762602056',
                first_name='Teacher',
                last_name='Sir',
                email='teacher01762602056@example.com',
                password_hash=generate_password_hash('sir@123@'),
                role=UserRole.TEACHER,
                is_active=True,
                sms_count=100  # Give teacher initial SMS balance
            )
            
            db.session.add(teacher)
            db.session.commit()
            
            print("✅ Teacher added successfully!")
            print(f"   Phone: {teacher.phoneNumber}")
            print(f"   Name: {teacher.full_name}")
            print(f"   Role: {teacher.role.value}")
            print(f"   Password: sir@123@")
            print(f"   SMS Balance: {teacher.sms_count}")
            print(f"   Login: Use phone number '01762602056' and password 'sir@123@'")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding teacher: {e}")
            return False

if __name__ == "__main__":
    print("Adding new teacher to the system...")
    add_teacher()