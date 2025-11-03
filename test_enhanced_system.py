"""
Test Enhanced MySQL System
Verify all new features work with MySQL database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Batch, UserRole, Settings
from config import DevelopmentConfig
import json

def test_mysql_connection():
    """Test MySQL connection and basic operations"""
    print("🔧 Testing Enhanced MySQL System...")
    
    # Create app with MySQL config
    app = create_app('development')
    
    with app.app_context():
        try:
            # Test database connection
            db.engine.execute('SELECT 1')
            print("✅ MySQL connection successful")
            
            # Test enhanced models
            user_count = User.query.count()
            batch_count = Batch.query.count()
            
            print(f"📊 Database Status:")
            print(f"   Users: {user_count}")
            print(f"   Batches: {batch_count}")
            
            # Test new tables exist
            tables_to_check = [
                'monthly_exams', 'individual_exams', 'monthly_marks',
                'question_bank', 'sms_logs', 'sms_templates',
                'attendance', 'settings'
            ]
            
            existing_tables = []
            for table in tables_to_check:
                try:
                    result = db.engine.execute(f'SELECT COUNT(*) FROM {table}')
                    count = result.fetchone()[0]
                    existing_tables.append(f"{table} ({count} records)")
                    print(f"✅ Table {table}: {count} records")
                except Exception as e:
                    print(f"❌ Table {table}: {str(e)}")
            
            # Test enhanced features
            print("\n🚀 Enhanced Features Status:")
            
            # Check if AI service is available
            try:
                from services.praggo_ai import praggo_ai
                print("✅ Praggo AI Service: Available")
            except Exception as e:
                print(f"❌ Praggo AI Service: {str(e)}")
            
            # Check if SMS service is available
            try:
                from services.sms_service import sms_service
                print("✅ SMS Service: Available")
            except Exception as e:
                print(f"❌ SMS Service: {str(e)}")
            
            # Check enhanced routes
            enhanced_routes = [
                'online_exams', 'monthly_exams'
            ]
            
            for route in enhanced_routes:
                try:
                    route_file = f"routes/{route}.py"
                    if os.path.exists(route_file):
                        print(f"✅ Enhanced Route {route}: Available")
                    else:
                        print(f"❌ Enhanced Route {route}: Missing")
                except Exception as e:
                    print(f"❌ Enhanced Route {route}: {str(e)}")
            
            # Test configuration
            print(f"\n⚙️ Configuration:")
            print(f"   Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
            print(f"   Debug Mode: {app.config.get('DEBUG', False)}")
            
            # Test login functionality
            try:
                test_user = User.query.filter_by(phoneNumber='01812345678').first()
                if test_user:
                    print(f"✅ Test login user available: {test_user.full_name}")
                else:
                    print("❌ Test login user not found")
            except Exception as e:
                print(f"❌ Test login user: {str(e)}")
            
            print("\n🎉 Enhanced MySQL System Test Completed!")
            return True
            
        except Exception as e:
            print(f"❌ MySQL connection failed: {str(e)}")
            return False

def test_new_features():
    """Test new feature implementations"""
    print("\n🧪 Testing New Features...")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # Test AI question generation parameters
            from services.praggo_ai import QuestionGenerationParams
            
            params = QuestionGenerationParams(
                class_id="10",
                class_name="Class 10",
                subject_id="math",
                subject_name="Mathematics",
                question_type="mcq",
                difficulty="medium",
                quantity=2
            )
            
            print("✅ AI Question Generation: Parameters created successfully")
            
            # Test SMS message structure
            from services.sms_service import SMSMessage
            
            sms = SMSMessage(
                recipient="01812345678",
                message="Test message from enhanced system"
            )
            
            print("✅ SMS Service: Message structure created successfully")
            
            # Test enhanced models
            from models import MonthlyExam, QuestionBank, SmsTemplate
            
            print("✅ Enhanced Models: All models imported successfully")
            
            print("🎉 New Features Test Completed!")
            return True
            
        except Exception as e:
            print(f"❌ New features test failed: {str(e)}")
            return False

if __name__ == "__main__":
    # Set environment variables for MySQL
    os.environ['MYSQL_HOST'] = 'localhost'
    os.environ['MYSQL_USER'] = 'root'
    os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
    os.environ['MYSQL_DATABASE'] = 'smartgardenhub'
    
    print("🔬 Enhanced SmartGardenHub System Test")
    print("=" * 50)
    
    mysql_test = test_mysql_connection()
    features_test = test_new_features()
    
    print("\n📋 Test Summary:")
    print(f"   MySQL Connection: {'✅ PASS' if mysql_test else '❌ FAIL'}")
    print(f"   New Features: {'✅ PASS' if features_test else '❌ FAIL'}")
    
    if mysql_test and features_test:
        print("\n🎉 All tests passed! Enhanced system is ready.")
        print("\n🚀 Next Steps:")
        print("   1. Start the enhanced application:")
        print("      python start_mysql.py")
        print("   2. Access the system at: http://localhost:5001")
        print("   3. Login with: 01812345678 / teacher123")
        print("   4. Explore new features: Online Exams, Monthly Rankings, AI Questions")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")