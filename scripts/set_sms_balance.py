#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, User, UserRole
from flask_bcrypt import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:sahidx%4012@localhost:3306/smartgardenhub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def set_teacher_sms_balance():
    with app.app_context():
        try:
            print("🔧 Setting SMS balance for teachers...")
            
            # Find teachers
            teachers = User.query.filter(
                User.role.in_([UserRole.TEACHER, UserRole.SUPER_USER]),
                User.is_active == True
            ).all()
            
            for teacher in teachers:
                print(f"📱 Teacher: {teacher.first_name} {teacher.last_name} ({teacher.phoneNumber})")
                print(f"📊 Current SMS balance: {teacher.sms_count}")
                
                # Set SMS balance to 100
                teacher.sms_count = 100
                print(f"✅ Updated SMS balance to: {teacher.sms_count}")
                print()
            
            db.session.commit()
            print("🎉 SMS balance updated successfully for all teachers!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    set_teacher_sms_balance()