#!/usr/bin/env python3
"""
Check user data for datetime issues
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from models import db, User, UserRole
from app import create_app

def check_user_data():
    """Check user data for potential serialization issues"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking User Data for Serialization Issues")
        print("-" * 50)
        
        # Find the super admin user
        user = User.query.filter_by(phoneNumber="01712345678").first()
        
        if not user:
            print("❌ User not found!")
            return
            
        print(f"User ID: {user.id}")
        print(f"Name: {user.first_name} {user.last_name}")
        print(f"Phone: {user.phoneNumber}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role} (type: {type(user.role)})")
        print(f"Role value: {user.role.value}")
        print(f"SMS Count: {user.sms_count}")
        print(f"Profile Image: {user.profile_image}")
        print(f"Last Login: {user.last_login} (type: {type(user.last_login)})")
        print(f"Created At: {user.created_at} (type: {type(user.created_at)})")
        print(f"Is Active: {user.is_active}")
        
        # Test datetime serialization
        try:
            if user.last_login:
                iso_last_login = user.last_login.isoformat()
                print(f"Last Login ISO: {iso_last_login}")
            else:
                print("Last Login ISO: None")
                
            if user.created_at:
                iso_created_at = user.created_at.isoformat()
                print(f"Created At ISO: {iso_created_at}")
            else:  
                print("Created At ISO: None")
                
        except Exception as e:
            print(f"❌ Datetime serialization error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_user_data()