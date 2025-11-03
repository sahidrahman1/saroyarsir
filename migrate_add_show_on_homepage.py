"""
Migration script to add show_on_homepage column to monthly_exams table
"""
from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    """Add show_on_homepage column to monthly_exams table"""
    app = create_app()
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('monthly_exams')]
            
            if 'show_on_homepage' in columns:
                print("✅ Column 'show_on_homepage' already exists in monthly_exams table")
                return
            
            # Add the column
            print("📝 Adding 'show_on_homepage' column to monthly_exams table...")
            db.session.execute(
                text('ALTER TABLE monthly_exams ADD COLUMN show_on_homepage BOOLEAN DEFAULT FALSE')
            )
            db.session.commit()
            print("✅ Successfully added 'show_on_homepage' column!")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
