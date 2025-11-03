"""
Reset all student passwords to last 4 digits of parent phone
"""
import sqlite3
from werkzeug.security import generate_password_hash

def reset_passwords():
    """Reset all student passwords to last 4 digits of parent phone"""
    try:
        conn = sqlite3.connect('smartgardenhub.db')
        cursor = conn.cursor()
        
        print("🔄 Resetting all student passwords...")
        
        # Get all students with guardian phone
        cursor.execute("""
            SELECT id, first_name, last_name, guardian_phone, phoneNumber 
            FROM users 
            WHERE role = 'student'
        """)
        
        students = cursor.fetchall()
        updated_count = 0
        
        for student_id, first_name, last_name, guardian_phone, phone_number in students:
            # Use guardian_phone if available, otherwise phoneNumber
            parent_phone = guardian_phone or phone_number
            
            if parent_phone and len(parent_phone) >= 4:
                # Generate password as last 4 digits
                new_password = parent_phone[-4:]
                password_hash = generate_password_hash(new_password)
                
                # Update password
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = ?
                    WHERE id = ?
                """, (password_hash, student_id))
                
                print(f"✅ Updated: {first_name} {last_name} - Phone: {parent_phone} - Password: {new_password}")
                updated_count += 1
            else:
                print(f"⚠️  Skipped: {first_name} {last_name} - No valid phone number")
        
        conn.commit()
        print(f"\n✅ Successfully updated {updated_count} student passwords!")
        print("\n📝 Password Format: Last 4 digits of parent phone number")
        print("🔑 Login: Parent Phone + Last 4 digits as password")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    reset_passwords()
