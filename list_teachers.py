#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import User, UserRole, db

def list_teachers():
    app = create_app()
    with app.app_context():
        try:
            teachers = User.query.filter_by(role=UserRole.TEACHER).all()
            
            print(f"📋 Found {len(teachers)} teacher(s) in the system:")
            print("=" * 60)
            
            for teacher in teachers:
                print(f"👨‍🏫 {teacher.full_name}")
                print(f"   📱 Phone: {teacher.phoneNumber}")
                print(f"   📧 Email: {teacher.email or 'Not set'}")
                print(f"   💬 SMS Balance: {teacher.sms_count}")
                print(f"   ✅ Active: {'Yes' if teacher.is_active else 'No'}")
                print(f"   📅 Created: {teacher.created_at.strftime('%Y-%m-%d %H:%M')}")
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ Error listing teachers: {e}")

if __name__ == "__main__":
    list_teachers()