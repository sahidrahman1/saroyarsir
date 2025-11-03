"""
SQLite Configuration for Development
Alternative database setup when MySQL is not available
"""
import os
import sqlite3
from pathlib import Path

def create_sqlite_database():
    """Create SQLite database for development"""
    db_path = Path("smartgardenhub.db")
    
    try:
        # Create connection
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print(f"✅ SQLite database created: {db_path.absolute()}")
        
        # Test the connection
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"📋 SQLite version: {version}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ SQLite setup failed: {e}")
        return False

def update_config_for_sqlite():
    """Update Flask config to use SQLite"""
    config_content = '''"""
Updated Configuration for SQLite Development
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    APP_NAME = 'SmartGardenHub'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_THRESHOLD = 500
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'

class DevelopmentConfig(Config):
    """Development configuration with SQLite"""
    DEBUG = True
    
    # SQLite database for development
    base_dir = Path(__file__).parent
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{base_dir}/smartgardenhub.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # MySQL for production
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'smartgardenhub')
    
    if MYSQL_PASSWORD:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    else:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    print("✅ Updated config.py for SQLite development")

def main():
    """Set up SQLite development environment"""
    print("🏗️  Setting up SQLite Development Environment")
    print("=" * 50)
    
    if create_sqlite_database():
        update_config_for_sqlite()
        print("\n✅ SQLite setup complete!")
        print("\nYou can now run:")
        print("  python run.py")
        print("\nThis will start the app with SQLite for development.")
        print("For production, install MySQL and update environment variables.")
        return True
    else:
        print("\n❌ SQLite setup failed")
        return False

if __name__ == '__main__':
    main()