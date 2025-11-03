#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import User, UserRole, db
from werkzeug.security import check_password_hash
import re

def debug_teacher_login():
    app = create_app()
    with app.app_context():
        try:
            print("🔍 Testing TEACHER login process...")
            
            # Step 1: Test phone validation
            phone = '01762602056'
            password = 'sir@123@'
            
            print(f"📱 Input phone: {phone}")
            print(f"🔑 Input password: {password}")
            
            # Phone validation function (copied from auth.py)
            def validate_phone(phone):
                phone = re.sub(r'[^\d]', '', phone)
                if phone.startswith('880'):
                    phone = phone[3:]
                elif phone.startswith('+880'):
                    phone = phone[4:]
                if len(phone) == 11 and phone.startswith('01'):
                    return phone
                return None
            
            formatted_phone = validate_phone(phone)
            print(f"📱 Formatted phone: {formatted_phone}")
            
            if not formatted_phone:
                print("❌ Phone validation failed!")
                return False
            
            # Step 2: Find user
            user = User.query.filter_by(phoneNumber=formatted_phone).first()
            print(f"👤 User found: {'Yes' if user else 'No'}")
            
            if not user:
                print("❌ User not found in database!")
                # List all teachers in database
                teachers = User.query.filter_by(role=UserRole.TEACHER).all()
                print(f"📋 Found {len(teachers)} teachers in database:")
                for t in teachers:
                    print(f"   - {t.full_name}: {t.phoneNumber}")
                return False
            
            print(f"   User ID: {user.id}")
            print(f"   User Name: {user.full_name}")
            print(f"   User Role: {user.role.value}")
            print(f"   User Active: {user.is_active}")
            
            # Step 3: Check if active
            if not user.is_active:
                print("❌ User is not active!")
                return False
            
            # Step 4: Password validation
            print(f"🔑 Testing password...")
            print(f"   Has password hash: {'Yes' if user.password_hash else 'No'}")
            print(f"   Password hash length: {len(user.password_hash) if user.password_hash else 0}")
            
            if user.role == UserRole.TEACHER:
                if user.password_hash:
                    password_valid = check_password_hash(user.password_hash, password)
                    print(f"   Password valid: {'Yes' if password_valid else 'No'}")
                    
                    if not password_valid:
                        print("❌ Password validation failed!")
                        # Try to test with different passwords
                        print("🔍 Testing other possible passwords...")
                        test_passwords = ['sir@123@', 'sir123', 'teacher123', 'admin123']
                        for test_pwd in test_passwords:
                            test_result = check_password_hash(user.password_hash, test_pwd)
                            print(f"   '{test_pwd}': {'✅' if test_result else '❌'}")
                        return False
                else:
                    print("❌ No password hash found!")
                    return False
            
            print("✅ All validation steps passed!")
            print("🎉 Teacher login should work!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during debug: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    debug_teacher_login()