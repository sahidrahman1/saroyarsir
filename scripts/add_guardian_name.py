"""
Add guardian_name column to users table
"""
import os
os.environ['FLASK_ENV'] = 'mysql'
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db

app = create_app('development')

with app.app_context():
    try:
        # Add guardian_name column
        db.engine.execute('ALTER TABLE users ADD COLUMN guardian_name VARCHAR(200) NULL AFTER address')
        print('✅ Successfully added guardian_name column to users table')
    except Exception as e:
        if 'Duplicate column name' in str(e):
            print('ℹ️  Column guardian_name already exists')
        else:
            print(f'❌ Error: {e}')
