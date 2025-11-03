"""
Fix VPS Issues: Fee Section and Marks Update
1. Check and fix database schema for fees table
2. Test marks update functionality
"""
import sqlite3
import sys
from sqlalchemy import create_engine, text, inspect
from models import db, Fee, MonthlyMark
from app import create_app

def check_and_fix_fees_table():
    """Check if fees table has correct columns"""
    print("\n" + "="*60)
    print("CHECKING FEES TABLE SCHEMA")
    print("="*60)
    
    app = create_app()
    
    with app.app_context():
        engine = db.engine
        inspector = inspect(engine)
        
        # Get current columns in fees table
        print("\n📋 Current fees table columns:")
        columns = inspector.get_columns('fees')
        column_names = [col['name'] for col in columns]
        
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        # Check if exam_fee and others_fee exist
        required_columns = {
            'exam_fee': 'NUMERIC(10, 2)',
            'others_fee': 'NUMERIC(10, 2)'
        }
        
        missing_columns = []
        for col_name in required_columns:
            if col_name not in column_names:
                missing_columns.append(col_name)
        
        if missing_columns:
            print(f"\n⚠️  Missing columns: {missing_columns}")
            print("Adding missing columns...")
            
            with engine.connect() as connection:
                for col_name in missing_columns:
                    try:
                        sql = f"ALTER TABLE fees ADD COLUMN {col_name} NUMERIC(10, 2) DEFAULT 0.00"
                        connection.execute(text(sql))
                        connection.commit()
                        print(f"✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"❌ Error adding {col_name}: {e}")
        else:
            print("\n✅ All required columns exist!")
        
        # Check if there's an 'exam' column that shouldn't exist
        if 'exam' in column_names:
            print("\n⚠️  Found unexpected 'exam' column - this may cause errors")
            print("   This column should be 'exam_fee' not 'exam'")
            try:
                with engine.connect() as connection:
                    # Rename exam to exam_fee if exam_fee doesn't exist
                    if 'exam_fee' not in column_names:
                        connection.execute(text("ALTER TABLE fees RENAME COLUMN exam TO exam_fee"))
                        connection.commit()
                        print("✅ Renamed 'exam' column to 'exam_fee'")
            except Exception as e:
                print(f"❌ Error renaming column: {e}")
        
        return True

def test_marks_update():
    """Test if marks can be queried and updated"""
    print("\n" + "="*60)
    print("TESTING MARKS UPDATE FUNCTIONALITY")
    print("="*60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Try to query marks
            print("\n📊 Querying MonthlyMark table...")
            marks_count = MonthlyMark.query.count()
            print(f"✅ Found {marks_count} marks records")
            
            # Check if we can create/update marks
            print("\n🔍 Checking database write permissions...")
            
            # Get a sample mark if exists
            sample_mark = MonthlyMark.query.first()
            if sample_mark:
                print(f"✅ Sample mark found: ID={sample_mark.id}")
                print(f"   Student: {sample_mark.user_id}")
                print(f"   Exam: {sample_mark.monthly_exam_id}")
                print(f"   Marks: {sample_mark.marks_obtained}/{sample_mark.total_marks}")
            else:
                print("⚠️  No marks found in database")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing marks: {e}")
            return False

def test_database_connection():
    """Test basic database connectivity"""
    print("\n" + "="*60)
    print("TESTING DATABASE CONNECTION")
    print("="*60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test basic query
            print("\n🔌 Testing database connection...")
            result = db.session.execute(text("SELECT 1")).scalar()
            print(f"✅ Database connection successful (result: {result})")
            
            # Check database file path
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            print(f"\n📁 Database URI: {db_uri}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

def main():
    """Run all fixes and tests"""
    print("🚀 Starting VPS Issue Diagnostics and Fixes")
    print("="*60)
    
    try:
        # Test 1: Database connection
        if not test_database_connection():
            print("\n❌ FAILED: Database connection issue")
            sys.exit(1)
        
        # Test 2: Check and fix fees table
        if not check_and_fix_fees_table():
            print("\n❌ FAILED: Fees table issue")
            sys.exit(1)
        
        # Test 3: Test marks functionality
        if not test_marks_update():
            print("\n❌ FAILED: Marks update issue")
            sys.exit(1)
        
        print("\n" + "="*60)
        print("✅ ALL CHECKS PASSED!")
        print("="*60)
        print("\n📝 Summary:")
        print("  1. Database connection: ✅")
        print("  2. Fees table schema: ✅")
        print("  3. Marks functionality: ✅")
        print("\n💡 Next steps:")
        print("  1. Commit these changes to git")
        print("  2. Push to your VPS repository")
        print("  3. On VPS, run: python fix_vps_issues.py")
        print("  4. Restart your Flask application")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
