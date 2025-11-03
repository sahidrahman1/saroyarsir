#!/usr/bin/env python3
"""
MySQL Database Setup Script
Initializes the SmartGardenHub database with MySQL
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from models import db, User, UserRole, Batch
from datetime import date, datetime
from decimal import Decimal
import bcrypt

def setup_mysql_database():
    """Initialize MySQL database with sample data"""
    
    # Set MySQL environment variables if not already set
    if not os.environ.get('MYSQL_HOST'):
        print("⚙️ Setting up MySQL environment variables...")
        print("Please set the following environment variables:")
        print("  MYSQL_HOST=localhost")
        print("  MYSQL_USER=root")
        print("  MYSQL_PASSWORD=your_password")
        print("  MYSQL_DATABASE=smartgardenhub")
        print("\nExample:")
        print("  $env:MYSQL_HOST='localhost'")
        print("  $env:MYSQL_USER='root'")
        print("  $env:MYSQL_PASSWORD='password123'")
        print("  $env:MYSQL_DATABASE='smartgardenhub'")
        
        # Prompt for values
        host = input("\nEnter MySQL host (default: localhost): ").strip() or 'localhost'
        user = input("Enter MySQL user (default: root): ").strip() or 'root'
        password = input("Enter MySQL password: ").strip()
        database = input("Enter database name (default: smartgardenhub): ").strip() or 'smartgardenhub'
        
        os.environ['MYSQL_HOST'] = host
        os.environ['MYSQL_USER'] = user
        os.environ['MYSQL_PASSWORD'] = password
        os.environ['MYSQL_DATABASE'] = database
    
    # Set config to use MySQL
    os.environ['FLASK_ENV'] = 'mysql'
    
    try:
        # Test MySQL connection first
        import pymysql
        connection = pymysql.connect(
            host=os.environ['MYSQL_HOST'],
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASSWORD'],
            port=int(os.environ.get('MYSQL_PORT', 3306))
        )
        
        # Create database if it doesn't exist
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.environ['MYSQL_DATABASE']}")
            print(f"✅ Database '{os.environ['MYSQL_DATABASE']}' created/verified")
        
        connection.close()
        
        # Initialize the Flask app with MySQL
        app = create_app('mysql')
        
        with app.app_context():
            print("🗄️ Creating MySQL tables...")
            
            # Drop all tables and recreate
            db.drop_all()
            db.create_all()
            
            print("✅ MySQL tables created successfully!")
            
            # Create sample users
            print("👥 Creating sample users...")
            
            # Hash passwords
            teacher_password = bcrypt.hashpw("teacher123".encode('utf-8'), bcrypt.gensalt())
            student_password = bcrypt.hashpw("student123".encode('utf-8'), bcrypt.gensalt())
            admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            
            # Create teacher
            teacher = User(
                phone="01812345678",
                first_name="Sample",
                last_name="Teacher",
                email="teacher@smartgardenhub.com",
                password_hash=teacher_password.decode('utf-8'),
                role=UserRole.TEACHER,
                is_active=True
            )
            
            # Create student
            student = User(
                phone="01912345678",
                first_name="Sample",
                last_name="Student",
                email="student@smartgardenhub.com",
                password_hash=student_password.decode('utf-8'),
                role=UserRole.STUDENT,
                guardian_phone="01712345679",
                is_active=True
            )
            
            # Create admin
            admin = User(
                phone="01712345678",
                first_name="Super",
                last_name="Admin",
                email="admin@smartgardenhub.com",
                password_hash=admin_password.decode('utf-8'),
                role=UserRole.SUPER_USER,
                is_active=True
            )
            
            db.session.add_all([teacher, student, admin])
            
            # Create sample batches
            print("📚 Creating sample batches...")
            
            batch1 = Batch(
                name="Class 10 - Science",
                subject="science",
                description="Class 10 Science batch for HSC preparation",
                start_date=date.today(),
                fee_amount=Decimal('2000.00'),
                status='active',
                is_active=True,
                max_students=50,
                class_time="10:00 AM - 12:00 PM",
                class_days="Sat, Mon, Wed"
            )
            
            batch2 = Batch(
                name="HSC - Higher Math",
                subject="higher math",
                description="Advanced mathematics for HSC students",
                start_date=date.today(),
                fee_amount=Decimal('2500.00'),
                status='active',
                is_active=True,
                max_students=30,
                class_time="2:00 PM - 4:00 PM",
                class_days="Sun, Tue, Thu"
            )
            
            batch3 = Batch(
                name="Grade 9 - Math Foundation",
                subject="math",
                description="Foundation mathematics for grade 9 students",
                start_date=date.today(),
                fee_amount=Decimal('1500.00'),
                status='active',
                is_active=True,
                max_students=40,
                class_time="4:00 PM - 6:00 PM",
                class_days="Sat, Mon, Wed, Fri"
            )
            
            db.session.add_all([batch1, batch2, batch3])
            
            # Enroll student in batch1
            student.batches.append(batch1)
            
            db.session.commit()
            
            print("✅ Sample data created successfully!")
            print("\n" + "="*50)
            print("🚀 MySQL Database setup completed!")
            print("="*50)
            print("📍 MySQL Connection:")
            print(f"   Host: {os.environ['MYSQL_HOST']}")
            print(f"   Database: {os.environ['MYSQL_DATABASE']}")
            print(f"   User: {os.environ['MYSQL_USER']}")
            print("\n🔐 Login Credentials:")
            print("   Teacher: 01812345678 / teacher123")
            print("   Student: 01912345678 / student123")
            print("   Admin: 01712345678 / admin123")
            print("\n📚 Sample Batches Created:")
            print("   - Class 10 - Science")
            print("   - HSC - Higher Math")
            print("   - Grade 9 - Math Foundation")
            print("="*50)
            
    except ImportError:
        print("❌ PyMySQL not installed. Installing...")
        os.system("pip install pymysql")
        print("✅ PyMySQL installed. Please run the script again.")
        
    except Exception as e:
        print(f"❌ Error setting up MySQL database: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check your MySQL credentials")
        print("3. Ensure the user has database creation privileges")
        print("4. Verify network connectivity to MySQL server")

if __name__ == "__main__":
    setup_mysql_database()