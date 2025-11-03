"""
Migration: Add admission_date column to users table
This adds the admission date field for tracking when students joined
"""
import sqlite3
import sys
from datetime import datetime

def migrate():
    """Add admission_date column to users table"""
    try:
        # Connect to database
        conn = sqlite3.connect('instance/smartgardenhub.db')
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'admission_date' not in columns:
            print("Adding admission_date column...")
            cursor.execute(
                "ALTER TABLE users ADD COLUMN admission_date DATE"
            )
            conn.commit()
            print("✓ admission_date column added successfully")
        else:
            print("✓ admission_date column already exists")
        
        conn.close()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
