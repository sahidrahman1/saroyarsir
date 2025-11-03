"""
Migration Script: Add Archive Fields to Users and Batches
This script adds archive-related columns to existing database tables
"""
from app import create_app
from models import db
from sqlalchemy import text
import os

def run_migration():
    """Add archive fields to users and batches tables"""
    
    # Determine environment
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    
    with app.app_context():
        try:
            print("🔄 Starting archive fields migration...")
            
            # Check if using SQLite or MySQL
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            is_sqlite = 'sqlite' in db_url.lower()
            
            print(f"📊 Database: {'SQLite' if is_sqlite else 'MySQL'}")
            
            # Add archive fields to users table
            print("\n📝 Adding archive fields to users table...")
            
            users_columns = [
                "ALTER TABLE users ADD COLUMN is_archived BOOLEAN DEFAULT 0 NOT NULL",
                "ALTER TABLE users ADD COLUMN archived_at DATETIME NULL",
                "ALTER TABLE users ADD COLUMN archived_by INTEGER NULL",
                "ALTER TABLE users ADD COLUMN archive_reason TEXT NULL"
            ]
            
            for sql in users_columns:
                try:
                    db.session.execute(text(sql))
                    column_name = sql.split('ADD COLUMN')[1].split()[0]
                    print(f"  ✅ Added {column_name} to users")
                except Exception as e:
                    if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                        column_name = sql.split('ADD COLUMN')[1].split()[0]
                        print(f"  ⏭️  {column_name} already exists in users")
                    else:
                        print(f"  ❌ Error adding column to users: {e}")
            
            # Add archive fields to batches table
            print("\n📝 Adding archive fields to batches table...")
            
            batches_columns = [
                "ALTER TABLE batches ADD COLUMN is_archived BOOLEAN DEFAULT 0 NOT NULL",
                "ALTER TABLE batches ADD COLUMN archived_at DATETIME NULL",
                "ALTER TABLE batches ADD COLUMN archived_by INTEGER NULL",
                "ALTER TABLE batches ADD COLUMN archive_reason TEXT NULL"
            ]
            
            for sql in batches_columns:
                try:
                    db.session.execute(text(sql))
                    column_name = sql.split('ADD COLUMN')[1].split()[0]
                    print(f"  ✅ Added {column_name} to batches")
                except Exception as e:
                    if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                        column_name = sql.split('ADD COLUMN')[1].split()[0]
                        print(f"  ⏭️  {column_name} already exists in batches")
                    else:
                        print(f"  ❌ Error adding column to batches: {e}")
            
            # Commit changes
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            print("\n📊 Archive System Features Added:")
            print("  • Teachers can archive batches")
            print("  • Teachers can archive individual students")
            print("  • Archived items are hidden from active views")
            print("  • Archived items can be restored")
            print("  • When batch is archived, all students are also archived")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {e}")
            return False

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
