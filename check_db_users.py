#!/usr/bin/env python3
"""
Check users in database
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from models import db, User, UserRole
from app import create_app

def check_users():
    """Check what users exist in database"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking users in database:")
        print("-" * 50)
        
        users = User.query.all()
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Name: {user.first_name} {user.last_name}")
            print(f"Phone: {user.phoneNumber}")
            print(f"Role: {user.role.value}")
            print(f"SMS Count: {user.sms_count}")
            print(f"Password Hash: {user.password_hash[:20] if user.password_hash else 'None'}...")
            print(f"Active: {user.is_active}")
            print("-" * 30)

if __name__ == "__main__":
    check_users()