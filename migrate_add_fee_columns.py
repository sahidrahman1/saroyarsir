"""
Migration: Add exam_fee and others_fee columns to Fee table
"""
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if columns already exist
        result = db.session.execute(text("PRAGMA table_info(fees)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'exam_fee' not in columns:
            print("Adding exam_fee column...")
            db.session.execute(text(
                "ALTER TABLE fees ADD COLUMN exam_fee NUMERIC(10, 2) DEFAULT 0.00"
            ))
            print("✓ exam_fee column added")
        else:
            print("✓ exam_fee column already exists")
        
        if 'others_fee' not in columns:
            print("Adding others_fee column...")
            db.session.execute(text(
                "ALTER TABLE fees ADD COLUMN others_fee NUMERIC(10, 2) DEFAULT 0.00"
            ))
            print("✓ others_fee column added")
        else:
            print("✓ others_fee column already exists")
        
        db.session.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.session.rollback()
