#!/usr/bin/env python3
"""
Test the auth system directly to find the error
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from models import db, User, UserRole
from app import create_app
from flask_bcrypt import check_password_hash

def test_auth_directly():
    """Test authentication logic directly"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Testing Auth System Directly")
        print("-" * 40)
        
        # Find the super admin user
        user = User.query.filter_by(phoneNumber="01712345678").first()
        
        if not user:
            print("❌ User not found!")
            return
            
        print(f"✅ User found: {user.first_name} {user.last_name}")
        print(f"Role: {user.role.value}")
        print(f"Phone: {user.phoneNumber}")
        print(f"Active: {user.is_active}")
        print(f"Password hash: {user.password_hash[:50] if user.password_hash else 'None'}...")
        
        # Test password check
        test_password = "admin123"
        print(f"\n🔐 Testing password: {test_password}")
        
        try:
            if user.password_hash:
                result = check_password_hash(user.password_hash, test_password)
                print(f"Password check result: {result}")
            else:
                print("❌ No password hash found!")
        except Exception as e:
            print(f"❌ Password check error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_auth_directly()