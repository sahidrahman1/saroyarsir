"""
Database Setup Script
Creates MySQL database and tables for SmartGardenHub
"""
import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set up basic environment
os.environ['DB_PASSWORD'] = ''  # No password for local MySQL
os.environ['DB_NAME'] = 'smartgardenhub'

def create_database():
    """Create the MySQL database if it doesn't exist"""
    import pymysql
    
    try:
        # Connect to MySQL server (not specific database)
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS smartgardenhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Database 'smartgardenhub' created or already exists")
            
            # Show databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"📋 Available databases: {[db[0] for db in databases]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def create_tables():
    """Create all application tables"""
    try:
        from app import create_app
        from models import db
        
        # Create app and tables
        app = create_app('development')
        with app.app_context():
            print("🏗️  Creating database tables...")
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Show tables
            from services.database import execute_query
            tables = execute_query("SHOW TABLES")
            print(f"📋 Created tables: {[list(table.values())[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

def initialize_data():
    """Initialize with sample data"""
    try:
        from init_db import main as init_db_main
        print("🌱 Initializing sample data...")
        init_db_main()
        print("✅ Sample data initialized!")
        return True
        
    except Exception as e:
        print(f"❌ Data initialization failed: {e}")
        return False

def main():
    """Main setup process"""
    print("🏫 SmartGardenHub Database Setup")
    print("=" * 40)
    
    steps = [
        ("Creating Database", create_database),
        ("Creating Tables", create_tables),
        ("Initializing Data", initialize_data)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}:")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return 1
    
    print("\n" + "=" * 40)
    print("✅ Database setup completed successfully!")
    print("\nYou can now run the application with:")
    print("  python run.py")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())