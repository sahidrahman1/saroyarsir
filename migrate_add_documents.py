"""
Migration script to add documents table for PDF storage
"""
from app import create_app
from models import db
import os

def migrate():
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Adding documents table for PDF storage...")
        print("=" * 60)
        
        # Create documents table
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name VARCHAR(200) NOT NULL,
                    book_name VARCHAR(200) NOT NULL,
                    chapter_name VARCHAR(200) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type VARCHAR(50) NOT NULL DEFAULT 'application/pdf',
                    description TEXT,
                    uploaded_by INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    download_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (uploaded_by) REFERENCES users (id)
                )
            """))
            conn.commit()
        
        print("✅ Documents table created successfully!")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'documents')
        os.makedirs(uploads_dir, exist_ok=True)
        print(f"✅ Uploads directory created: {uploads_dir}")
        
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)

if __name__ == '__main__':
    migrate()
