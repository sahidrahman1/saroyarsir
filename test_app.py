#!/usr/bin/env python3
"""
Quick Test Script for SmartGardenHub Python Application
Test basic functionality and imports
"""
import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test that all critical modules can be imported"""
    print("🧪 Testing Python imports...")
    
    try:
        # Test Flask app creation
        print("  - Testing Flask app...")
        from app import create_app
        app = create_app('development')
        print("  ✅ Flask app created successfully")
        
        # Test database models
        print("  - Testing database models...")
        from models import User, Batch, Exam, db
        print("  ✅ Database models imported successfully")
        
        # Test AI service
        print("  - Testing AI service...")
        from services.praggo_ai import QuestionGenerationParams, AISolveParams
        print("  ✅ AI service imported successfully")
        
        # Test database service
        print("  - Testing database service...")
        from services.database import health_check, get_db_session
        print("  ✅ Database service imported successfully")
        
        # Test routes
        print("  - Testing route modules...")
        from routes.auth import auth_bp
        from routes.ai import ai_bp
        from routes.users import users_bp
        print("  ✅ All route modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_configuration():
    """Test application configuration"""
    print("🔧 Testing configuration...")
    
    try:
        from config import config_by_name
        dev_config = config_by_name['development']
        print(f"  ✅ Development config loaded: {dev_config}")
        return True
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("🗄️  Testing database connection...")
    
    try:
        from services.database import health_check
        result = health_check()
        
        if result.get('status') == 'healthy':
            print("  ✅ Database connection successful")
            print(f"  📊 Database: {result.get('database')}")
            print(f"  📈 Response time: {result.get('response_time_ms')}ms")
            return True
        else:
            print(f"  ⚠️  Database unhealthy: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ Database connection error: {e}")
        return False

def main():
    """Run all tests"""
    print("🏫 SmartGardenHub Python Application Test")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database", test_database_connection)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The Python application is ready to run.")
        print("\nTo start the application, run:")
        print("  python run.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())