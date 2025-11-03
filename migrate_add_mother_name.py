"""
Migration Script: Add mother_name field to users table
"""
import sqlite3
import sys

def migrate_database():
    """Add mother_name column to users table"""
    try:
        # Connect to database
        conn = sqlite3.connect('smartgardenhub.db')
        cursor = conn.cursor()
        
        print("🔄 Starting migration: Add mother_name to users table...")
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'mother_name' in columns:
            print("✅ Column 'mother_name' already exists. Skipping...")
        else:
            print("📝 Adding 'mother_name' column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN mother_name VARCHAR(200)
            """)
            print("✅ Added 'mother_name' column successfully")
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show sample of the updated table structure
        print("\n📊 Updated users table structure:")
        cursor.execute("PRAGMA table_info(users)")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    migrate_database()
