#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, User, UserRole
from flask_bcrypt import check_password_hash, generate_password_hash
import re

def validate_phone(phone):
    """Validate Bangladeshi phone number format"""
    # Remove any spaces or special characters
    phone = re.sub(r'[^\d]', '', phone)
    
    # Check if it's a valid Bangladeshi number
    if phone.startswith('880'):
        phone = phone[3:]  # Remove country code
    elif phone.startswith('+880'):
        phone = phone[4:]  # Remove country code with +
    
    # Should be 11 digits starting with 01
    if len(phone) == 11 and phone.startswith('01'):
        return phone
    
    return None

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:sahidx%4012@localhost:3306/smartgardenhub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def debug_login():
    with app.app_context():
        try:
            print("🔍 Debugging student login...")
            
            phone = "01616161123"
            password = "541123"
            
            # Validate and format phone number
            formatted_phone = validate_phone(phone)
            print(f"📱 Original phone: {phone}")
            print(f"📱 Formatted phone: {formatted_phone}")
            
            if not formatted_phone:
                print("❌ Invalid phone number format")
                return
            
            # Find user by phone
            user = User.query.filter_by(phoneNumber=formatted_phone).first()
            
            if not user:
                print("❌ User not found")
                
                # Check what users exist
                all_users = User.query.all()
                print(f"\n📋 All users in database:")
                for u in all_users:
                    print(f"  - {u.phoneNumber} ({u.first_name} {u.last_name}) - Role: {u.role}")
                return
            
            print(f"✅ User found: {user.first_name} {user.last_name}")
            print(f"📱 Phone: {user.phoneNumber}")
            print(f"👤 Role: {user.role}")
            print(f"🔑 Has password_hash: {bool(user.password_hash)}")
            print(f"📊 Is active: {user.is_active}")
            
            if user.password_hash:
                print(f"🔐 Password hash: {user.password_hash[:50]}...")
            
            # Check password based on user role
            password_valid = False
            
            if user.role == UserRole.STUDENT:
                # For students, check if password matches "student123" (legacy) or hashed password (new unique passwords)
                legacy_check = (password == "student123")
                hash_check = check_password_hash(user.password_hash, password) if user.password_hash else False
                
                print(f"🔍 Legacy check (student123): {legacy_check}")
                print(f"🔍 Hash check ({password}): {hash_check}")
                
                password_valid = legacy_check or hash_check
            else:
                # For teachers and super users, check hashed password
                if user.password_hash:
                    password_valid = check_password_hash(user.password_hash, password)
                    print(f"🔍 Password valid: {password_valid}")
            
            print(f"✅ Final password validation: {password_valid}")
            
            if password_valid:
                print("🎉 Login would succeed!")
            else:
                print("❌ Login would fail!")
                
                # Try to set the correct password
                print(f"\n🔧 Setting password '{password}' for user...")
                user.password_hash = generate_password_hash(password)
                db.session.commit()
                print("✅ Password updated successfully!")
                
                # Test again
                new_check = check_password_hash(user.password_hash, password)
                print(f"🔍 New password check: {new_check}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_login()