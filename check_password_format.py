#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import User, UserRole, db

def check_password_hash_format():
    app = create_app()
    with app.app_context():
        try:
            # Get the teacher
            teacher = User.query.filter_by(phoneNumber='01762602056').first()
            
            if teacher and teacher.password_hash:
                print(f"Password hash: {teacher.password_hash}")
                print(f"Hash length: {len(teacher.password_hash)}")
                print(f"Hash starts with: {teacher.password_hash[:10]}")
                
                # Check hash format
                if teacher.password_hash.startswith('$2b$'):
                    print("✅ This is a bcrypt hash")
                elif teacher.password_hash.startswith('pbkdf2:'):
                    print("✅ This is a Werkzeug PBKDF2 hash")
                elif teacher.password_hash.startswith('scrypt:'):
                    print("✅ This is a Werkzeug scrypt hash")
                else:
                    print("❓ Unknown hash format")
                
                # Try both methods
                print("\n🔍 Testing with werkzeug.security:")
                try:
                    from werkzeug.security import check_password_hash
                    result1 = check_password_hash(teacher.password_hash, 'sir@123@')
                    print(f"   werkzeug.security result: {'✅ PASS' if result1 else '❌ FAIL'}")
                except Exception as e:
                    print(f"   werkzeug.security error: {e}")
                
                print("\n🔍 Testing with flask_bcrypt:")
                try:
                    from flask_bcrypt import check_password_hash
                    result2 = check_password_hash(teacher.password_hash, 'sir@123@')
                    print(f"   flask_bcrypt result: {'✅ PASS' if result2 else '❌ FAIL'}")
                except Exception as e:
                    print(f"   flask_bcrypt error: {e}")
                
            else:
                print("❌ Teacher or password hash not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_password_hash_format()