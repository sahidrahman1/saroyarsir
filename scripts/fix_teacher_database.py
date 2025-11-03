#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import User, UserRole, db
from werkzeug.security import generate_password_hash, check_password_hash

def fix_teacher_in_database():
    app = create_app()
    with app.app_context():
        try:
            # Find the teacher
            teacher = User.query.filter_by(phoneNumber='01762602056').first()
            
            if not teacher:
                print("❌ Teacher not found! Creating new teacher...")
                # Create new teacher
                teacher = User(
                    phoneNumber='01762602056',
                    first_name='Teacher',
                    last_name='Sir',
                    email='teacher01762602056@example.com',
                    password_hash=generate_password_hash('sir@123@'),
                    role=UserRole.TEACHER,
                    is_active=True,
                    sms_count=100
                )
                
                db.session.add(teacher)
                db.session.commit()
                print("✅ New teacher created successfully!")
            else:
                print(f"✅ Teacher found: {teacher.full_name}")
                print(f"   Phone: {teacher.phoneNumber}")
                print(f"   Role: {teacher.role.value}")
                print(f"   Active: {teacher.is_active}")
                print(f"   Has password hash: {'Yes' if teacher.password_hash else 'No'}")
                
                # Test password verification
                if teacher.password_hash:
                    test_password = check_password_hash(teacher.password_hash, 'sir@123@')
                    print(f"   Password 'sir@123@' matches: {'Yes' if test_password else 'No'}")
                    
                    if not test_password:
                        print("🔧 Fixing password hash...")
                        teacher.password_hash = generate_password_hash('sir@123@')
                        db.session.commit()
                        print("✅ Password hash updated!")
                        
                        # Test again
                        test_password_new = check_password_hash(teacher.password_hash, 'sir@123@')
                        print(f"   Password now matches: {'Yes' if test_password_new else 'No'}")
                else:
                    print("🔧 Adding password hash...")
                    teacher.password_hash = generate_password_hash('sir@123@')
                    db.session.commit()
                    print("✅ Password hash added!")
            
            # Final verification
            print("\n🔍 Final Teacher Status:")
            teacher_final = User.query.filter_by(phoneNumber='01762602056').first()
            if teacher_final:
                print(f"   ID: {teacher_final.id}")
                print(f"   Name: {teacher_final.full_name}")
                print(f"   Phone: {teacher_final.phoneNumber}")
                print(f"   Role: {teacher_final.role.value}")
                print(f"   Active: {teacher_final.is_active}")
                print(f"   Email: {teacher_final.email}")
                print(f"   SMS Count: {teacher_final.sms_count}")
                print(f"   Password Hash Length: {len(teacher_final.password_hash) if teacher_final.password_hash else 0}")
                
                # Test login credentials
                password_works = check_password_hash(teacher_final.password_hash, 'sir@123@')
                print(f"   Login Test: {'✅ PASS' if password_works else '❌ FAIL'}")
                
                return True
            else:
                print("❌ Teacher still not found after fix!")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🔧 Fixing teacher in database...")
    success = fix_teacher_in_database()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Teacher database fix completed!")