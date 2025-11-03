"""
Fix specific student password for phone 01616161123
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, User, UserRole
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

with app.app_context():
    try:
        phone = '01616161123'
        new_password = '541123'  # The password user is trying to use
        
        print(f"🔧 Fixing password for student: {phone}")
        print(f"🔑 Setting password to: {new_password}")
        print("=" * 50)
        
        user = User.query.filter_by(phoneNumber=phone).first()
        
        if user:
            print(f"✅ User found: {user.full_name}")
            
            # Update password
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            
            print(f"✅ Password updated successfully!")
            
            # Test the new password
            print(f"\n🧪 Testing new password...")
            if check_password_hash(user.password_hash, new_password):
                print(f"✅ Password verification successful!")
            else:
                print(f"❌ Password verification failed!")
                
            print(f"\n📋 UPDATED CREDENTIALS:")
            print(f"   📞 Phone: {user.phoneNumber}")
            print(f"   👤 Name: {user.full_name}")
            print(f"   🔑 Password: {new_password}")
            print(f"   🎭 Role: {user.role}")
            print(f"   🟢 Active: {user.is_active}")
            
        else:
            print(f"❌ No user found with phone: {phone}")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()