#!/usr/bin/env python3
"""
Fix VPS Database Issues:
1. Ensure archived students have correct is_archived flag
2. Verify database schema consistency
3. Check monthly exam data
"""

import sqlite3
from datetime import datetime

def fix_database():
    """Fix database issues on VPS"""
    db_path = 'madrasha.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("DATABASE FIX SCRIPT")
        print("=" * 60)
        
        # 1. Check and fix archived students
        print("\n1. Checking archived students...")
        cursor.execute("""
            SELECT id, phoneNumber, first_name, last_name, is_archived, archived_at 
            FROM users 
            WHERE role = 'STUDENT'
        """)
        students = cursor.fetchall()
        
        print(f"   Total students: {len(students)}")
        
        archived_count = 0
        for student in students:
            student_id, phone, first_name, last_name, is_archived, archived_at = student
            if is_archived or archived_at is not None:
                archived_count += 1
                print(f"   ✓ Archived: {first_name} {last_name} (ID: {student_id}, Phone: {phone})")
                print(f"     is_archived={is_archived}, archived_at={archived_at}")
        
        print(f"   Found {archived_count} archived students")
        
        # 2. Check for students that should be archived but aren't
        print("\n2. Looking for inconsistencies...")
        cursor.execute("""
            SELECT id, phoneNumber, first_name, last_name, is_archived, archived_at 
            FROM users 
            WHERE role = 'STUDENT' 
            AND (
                (is_archived = 1 AND archived_at IS NULL) 
                OR (is_archived = 0 AND archived_at IS NOT NULL)
            )
        """)
        inconsistent = cursor.fetchall()
        
        if inconsistent:
            print(f"   ⚠️  Found {len(inconsistent)} inconsistent records:")
            for student in inconsistent:
                student_id, phone, first_name, last_name, is_archived, archived_at = student
                print(f"      {first_name} {last_name} - is_archived={is_archived}, archived_at={archived_at}")
                
                # Fix: If archived_at is set, is_archived should be True
                if archived_at is not None and not is_archived:
                    print(f"      → Fixing: Setting is_archived=1 for student {student_id}")
                    cursor.execute("UPDATE users SET is_archived = 1 WHERE id = ?", (student_id,))
        else:
            print("   ✓ No inconsistencies found")
        
        # 3. Check monthly exams
        print("\n3. Checking monthly exams...")
        cursor.execute("""
            SELECT id, title, batch_id, year, month 
            FROM monthly_exams 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        exams = cursor.fetchall()
        
        print(f"   Recent monthly exams ({len(exams)}):")
        for exam in exams:
            exam_id, title, batch_id, year, month = exam
            print(f"   - ID {exam_id}: {title} (Batch {batch_id}, {year}-{month})")
        
        # 4. Check for orphaned data
        print("\n4. Checking for orphaned data...")
        
        # Check rankings without exams
        cursor.execute("""
            SELECT COUNT(*) 
            FROM monthly_rankings 
            WHERE monthly_exam_id NOT IN (SELECT id FROM monthly_exams)
        """)
        orphaned_rankings = cursor.fetchone()[0]
        if orphaned_rankings > 0:
            print(f"   ⚠️  Found {orphaned_rankings} rankings without exams")
            print("      → Cleaning up...")
            cursor.execute("""
                DELETE FROM monthly_rankings 
                WHERE monthly_exam_id NOT IN (SELECT id FROM monthly_exams)
            """)
        else:
            print("   ✓ No orphaned rankings")
        
        # Check individual exams without monthly exams
        cursor.execute("""
            SELECT COUNT(*) 
            FROM individual_exams 
            WHERE monthly_exam_id NOT IN (SELECT id FROM monthly_exams)
        """)
        orphaned_individual = cursor.fetchone()[0]
        if orphaned_individual > 0:
            print(f"   ⚠️  Found {orphaned_individual} individual exams without monthly exams")
            print("      → Cleaning up...")
            cursor.execute("""
                DELETE FROM individual_exams 
                WHERE monthly_exam_id NOT IN (SELECT id FROM monthly_exams)
            """)
        else:
            print("   ✓ No orphaned individual exams")
        
        # 5. Verify schema has all required columns
        print("\n5. Verifying schema...")
        cursor.execute("PRAGMA table_info(users)")
        columns = {col[1] for col in cursor.fetchall()}
        
        required_columns = ['is_archived', 'archived_at', 'archived_by']
        missing = [col for col in required_columns if col not in columns]
        
        if missing:
            print(f"   ⚠️  Missing columns in users table: {missing}")
            for col in missing:
                if col == 'is_archived':
                    print(f"      → Adding {col}...")
                    cursor.execute("ALTER TABLE users ADD COLUMN is_archived BOOLEAN DEFAULT 0 NOT NULL")
                elif col == 'archived_at':
                    print(f"      → Adding {col}...")
                    cursor.execute("ALTER TABLE users ADD COLUMN archived_at DATETIME")
                elif col == 'archived_by':
                    print(f"      → Adding {col}...")
                    cursor.execute("ALTER TABLE users ADD COLUMN archived_by INTEGER")
        else:
            print("   ✓ All required columns present")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✓ DATABASE FIX COMPLETED")
        print("=" * 60)
        
        # Print summary
        print("\nSUMMARY:")
        print(f"- Total students: {len(students)}")
        print(f"- Archived students: {archived_count}")
        print(f"- Inconsistencies fixed: {len(inconsistent) if inconsistent else 0}")
        print(f"- Orphaned rankings cleaned: {orphaned_rankings}")
        print(f"- Orphaned individual exams cleaned: {orphaned_individual}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_database()
    exit(0 if success else 1)
