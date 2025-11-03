"""
Test login functionality
"""
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app import create_app
from models import User, UserRole
from flask_bcrypt import check_password_hash

app = create_app()

with app.app_context():
    # Test finding the teacher user
    teacher = User.query.filter_by(phoneNumber='01812345678').first()
    
    if teacher:
        print(f"✅ Found teacher: {teacher.first_name} {teacher.last_name}")
        print(f"Phone: {teacher.phoneNumber}")
        print(f"Role: {teacher.role}")
        print(f"Password hash exists: {bool(teacher.password_hash)}")
        print(f"Password hash length: {len(teacher.password_hash) if teacher.password_hash else 0}")
        
        # Test password verification
        if teacher.password_hash:
            try:
                password_valid = check_password_hash(teacher.password_hash, 'teacher123')
                print(f"Password 'teacher123' valid: {password_valid}")
            except Exception as e:
                print(f"❌ Error checking password: {e}")
        else:
            print("❌ No password hash found!")
    else:
        print("❌ Teacher user not found!")
        
    # List all users
    print("\nAll users:")
    users = User.query.all()
    for user in users:
        print(f"- {user.phoneNumber}: {user.first_name} {user.last_name} ({user.role.value})")