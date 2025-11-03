#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, User, UserRole
from flask_bcrypt import check_password_hash, generate_password_hash
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:sahidx%4012@localhost:3306/smartgardenhub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def fix_student_password():
    with app.app_context():
        try:
            print("🔧 Fixing student password...")
            
            phone = "01616161123"
            password = "541123"
            
            # Find user by phone
            user = User.query.filter_by(phoneNumber=phone).first()
            
            if not user:
                print("❌ User not found")
                return
            
            print(f"✅ User found: {user.first_name} {user.last_name}")
            print(f"📱 Phone: {user.phoneNumber}")
            
            # Generate a proper Flask-Bcrypt hash
            print(f"🔐 Setting password '{password}' with proper bcrypt hash...")
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            print("✅ Password hash updated successfully!")
            
            # Test the new hash
            test_result = check_password_hash(user.password_hash, password)
            print(f"🔍 Password verification test: {test_result}")
            
            if test_result:
                print("🎉 Password is now working correctly!")
            else:
                print("❌ Password still not working")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_student_password()