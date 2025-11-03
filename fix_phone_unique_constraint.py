#!/usr/bin/env python3
"""
Fix Phone Number Unique Constraint Issue

This script removes the UNIQUE constraint from the phoneNumber column
to allow multiple students (siblings) to share the same parent phone number.
"""

import sqlite3
import sys

def fix_phone_constraint():
    """Remove unique constraint from phoneNumber column"""
    db_path = 'madrasha.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("FIXING PHONE NUMBER UNIQUE CONSTRAINT")
        print("=" * 60)
        
        # Check current schema
        print("\n1. Checking current schema...")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("   Current columns in users table:")
        for col in columns:
            col_id, name, type_, notnull, default, pk = col
            print(f"     - {name}: {type_} (NOT NULL: {bool(notnull)}, PK: {bool(pk)})")
        
        # Check for unique constraint
        print("\n2. Checking for unique constraint on phoneNumber...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
        create_sql = cursor.fetchone()[0]
        
        if 'phoneNumber' in create_sql and 'UNIQUE' in create_sql.upper():
            print("   ⚠️  Found UNIQUE constraint on phoneNumber!")
            print("   → Need to recreate table without unique constraint")
            
            # SQLite doesn't support ALTER TABLE DROP CONSTRAINT
            # We need to recreate the table
            
            print("\n3. Creating backup of users table...")
            cursor.execute("CREATE TABLE users_backup AS SELECT * FROM users")
            backup_count = cursor.execute("SELECT COUNT(*) FROM users_backup").fetchone()[0]
            print(f"   ✓ Backed up {backup_count} users")
            
            print("\n4. Getting foreign key relationships...")
            cursor.execute("PRAGMA foreign_keys=OFF")
            
            print("\n5. Dropping old users table...")
            cursor.execute("DROP TABLE users")
            
            print("\n6. Creating new users table without unique constraint...")
            # Create table with phoneNumber as non-unique
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phoneNumber VARCHAR(20) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    password_hash VARCHAR(255),
                    role VARCHAR(20) NOT NULL DEFAULT 'STUDENT',
                    profile_image TEXT,
                    date_of_birth DATE,
                    address TEXT,
                    guardian_name VARCHAR(200),
                    guardian_phone VARCHAR(20),
                    mother_name VARCHAR(200),
                    emergency_contact VARCHAR(20),
                    admission_date DATE,
                    sms_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    last_login DATETIME,
                    is_archived BOOLEAN DEFAULT 0 NOT NULL,
                    archived_at DATETIME,
                    archived_by INTEGER,
                    archive_reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (archived_by) REFERENCES users(id)
                )
            """)
            
            print("\n7. Creating index on phoneNumber...")
            cursor.execute("CREATE INDEX idx_users_phoneNumber ON users(phoneNumber)")
            
            print("\n8. Restoring data from backup...")
            cursor.execute("""
                INSERT INTO users 
                SELECT * FROM users_backup
            """)
            restored_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            print(f"   ✓ Restored {restored_count} users")
            
            print("\n9. Dropping backup table...")
            cursor.execute("DROP TABLE users_backup")
            
            print("\n10. Re-enabling foreign keys...")
            cursor.execute("PRAGMA foreign_keys=ON")
            
            conn.commit()
            
            print("\n" + "=" * 60)
            print("✓ UNIQUE CONSTRAINT REMOVED SUCCESSFULLY")
            print("=" * 60)
            
        else:
            print("   ✓ No unique constraint found - phoneNumber is already non-unique")
        
        # Verify the fix
        print("\n11. Verification:")
        cursor.execute("""
            SELECT phoneNumber, COUNT(*) as count, GROUP_CONCAT(first_name || ' ' || last_name) as names
            FROM users 
            WHERE role = 'STUDENT'
            GROUP BY phoneNumber
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"   ✓ Found {len(duplicates)} phone numbers with multiple students (siblings):")
            for phone, count, names in duplicates:
                print(f"      {phone}: {count} students - {names}")
        else:
            print("   → No duplicate phone numbers yet (but now they can be created)")
        
        # Test: Try to create duplicate (this would fail with unique constraint)
        print("\n12. Testing: Can we have duplicate phone numbers?")
        cursor.execute("SELECT phoneNumber FROM users WHERE role='STUDENT' LIMIT 1")
        test_phone = cursor.fetchone()
        
        if test_phone:
            try:
                cursor.execute("""
                    INSERT INTO users (phoneNumber, first_name, last_name, role, is_active, is_archived)
                    VALUES (?, 'Test', 'Student', 'STUDENT', 1, 0)
                """, (test_phone[0],))
                cursor.execute("DELETE FROM users WHERE first_name='Test' AND last_name='Student'")
                conn.commit()
                print("   ✓ SUCCESS: Can create students with duplicate phone numbers!")
            except sqlite3.IntegrityError as e:
                print(f"   ✗ FAILED: {str(e)}")
                print("   → Unique constraint still exists!")
                conn.rollback()
                return False
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            conn.rollback()
        except:
            pass
        return False

if __name__ == '__main__':
    success = fix_phone_constraint()
    sys.exit(0 if success else 1)
