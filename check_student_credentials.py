"""
Check current student credentials in database
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, User, UserRole
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    try:
        # Check for the specific phone number from the screenshot
        phone_to_check = '01616161123'
        password_to_check = '541123'
        
        print(f"🔍 Checking login for phone: {phone_to_check}")
        print(f"🔑 Password attempting: {password_to_check}")
        print("=" * 50)
        
        user = User.query.filter_by(phoneNumber=phone_to_check).first()
        
        if user:
            print(f"✅ User found!")
            print(f"   📞 Phone: {user.phoneNumber}")
            print(f"   👤 Name: {user.full_name}")
            print(f"   🎭 Role: {user.role}")
            print(f"   🟢 Active: {user.is_active}")
            
            # Test password
            if check_password_hash(user.password_hash, password_to_check):
                print(f"   ✅ Password CORRECT for '{password_to_check}'")
            else:
                print(f"   ❌ Password INCORRECT for '{password_to_check}'")
                
                # Try to find what the actual password should be
                print(f"\n🔍 Let me check recent password updates...")
                
        else:
            print(f"❌ No user found with phone: {phone_to_check}")
            
        # List all students for reference
        print(f"\n📋 ALL STUDENTS IN DATABASE:")
        print("=" * 50)
        
        students = User.query.filter_by(role=UserRole.STUDENT, is_active=True).all()
        
        for student in students:
            print(f"👤 {student.full_name}")
            print(f"   📞 Phone: {student.phoneNumber}")
            print(f"   🎭 Role: {student.role}")
            print()
            
        print(f"Total students found: {len(students)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()