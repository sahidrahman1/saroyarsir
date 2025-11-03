#!/bin/bash

# Fix VPS to use SQLite instead of PostgreSQL
# This script updates the .env file and verifies the configuration

echo "=========================================="
echo "🔧 VPS SQLite Configuration Fix"
echo "=========================================="
echo ""

APP_DIR="/var/www/saroyarsir"
cd $APP_DIR || exit 1

echo "📂 Working directory: $(pwd)"
echo ""

# Backup existing .env if it exists
if [ -f .env ]; then
    echo "📋 Backing up existing .env file..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created"
else
    echo "ℹ️  No existing .env file found"
fi

echo ""
echo "🔧 Creating/Updating .env file for SQLite..."

# Create new .env with SQLite configuration
cat > .env << 'EOF'
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this-in-production

# Database Configuration - SQLite
DATABASE_URL=sqlite:///madrasha.db

# Application Settings
PORT=8000
HOST=0.0.0.0

# SMS Configuration (if applicable)
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=your-sender-id

# Session Configuration
SESSION_TYPE=filesystem
EOF

echo "✅ .env file created/updated with SQLite configuration"
echo ""

echo "📋 Current .env contents:"
cat .env
echo ""

echo "🔍 Verifying database file..."
if [ -f "madrasha.db" ]; then
    echo "✅ Database file 'madrasha.db' exists"
    DB_SIZE=$(du -h madrasha.db | cut -f1)
    echo "   Size: $DB_SIZE"
else
    echo "⚠️  Database file 'madrasha.db' not found"
    echo "   It will be created on first run"
fi

echo ""
echo "🧪 Testing database connection..."
python3 << 'PYTHON_TEST'
import os
os.environ['DATABASE_URL'] = 'sqlite:///madrasha.db'

try:
    from app import create_app
    from models import db
    
    app = create_app()
    
    with app.app_context():
        # Try to query the database
        from sqlalchemy import text
        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5"))
        tables = [row[0] for row in result]
        
        print("✅ Database connection successful!")
        print(f"   Found {len(tables)} tables: {', '.join(tables[:5])}")
        
        # Count users
        result = db.session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"   Total users: {user_count}")
        
        # Count students
        result = db.session.execute(text("SELECT COUNT(*) FROM users WHERE role='STUDENT'"))
        student_count = result.scalar()
        print(f"   Total students: {student_count}")
        
except Exception as e:
    print(f"❌ Database connection failed: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_TEST

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SQLite Configuration Complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Restart the service: sudo systemctl restart smartgardenhub"
    echo "2. Check status: sudo systemctl status smartgardenhub"
    echo "3. View logs: sudo journalctl -u smartgardenhub -n 50"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ Configuration failed - see errors above"
    echo "=========================================="
    exit 1
fi
