#!/usr/bin/env python3
"""
Test    print("   Student: 01912345678 / [Unique Password] (Parent Phone / Password)")
    print("   Admin: 01712345678 / admin123")
    print()
    print("📝 Note: Students login with their PARENT PHONE NUMBER + unique generated password")rtGardenHub with MySQL
"""
import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set MySQL environment variables
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

try:
    from app import create_app
    
    print("🐬 Starting SmartGardenHub with MySQL...")
    app = create_app('development')  # Use development config with MySQL
    
    # Test database connection
    with app.app_context():
        from models import db
        print("✅ MySQL connection successful!")
        print(f"📊 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    print(f"📍 Server will be available at: http://127.0.0.1:5001")
    print("🔐 Login with:")
    print("   Teacher: 01812345678 / teacher123")
    print("   Student: 01912345678 / [Unique Password] (Parent Phone / Password)")
    print("   Admin: 01712345678 / admin123")
    print("")
    print("📝 Note: Students login with their PARENT PHONE NUMBER + unique generated password")
    print("🏫 GS Student Nursing Center by Golam Sarowar Sir - Mathematics & Science Coaching Center")
    print("=" * 50)
    
    app.run(
        host='127.0.0.1',
        port=5001,  # Use different port
        debug=True,
        use_reloader=False,
        threaded=True
    )
    
except Exception as e:
    print(f"❌ Error starting Flask app with MySQL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)