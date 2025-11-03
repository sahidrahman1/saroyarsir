#!/usr/bin/env python3
"""
Test MySQL Connection for SmartGardenHub
"""
import os
import pymysql

def test_mysql_connection():
    """Test connection to MySQL with current environment variables"""
    
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DATABASE', 'smartgardenhub')
    port = int(os.environ.get('MYSQL_PORT', 3306))
    
    print("🔍 Testing MySQL Connection...")
    print(f"   Host: {host}")
    print(f"   User: {user}")
    print(f"   Database: {database}")
    print(f"   Port: {port}")
    print(f"   Password: {'Set' if password else 'Empty'}")
    print("")
    
    try:
        # Test connection
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        
        print("✅ MySQL connection successful!")
        
        # Test database creation
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            print(f"✅ Database '{database}' created/verified")
            
            cursor.execute(f"USE {database}")
            print(f"✅ Using database '{database}'")
        
        connection.close()
        print("✅ MySQL is ready for SmartGardenHub!")
        return True
        
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check if the password is correct")
        print("3. Verify user has proper privileges")
        
        if "Access denied" in str(e):
            print("\n💡 Common solutions:")
            print("   - Set correct password: $env:MYSQL_PASSWORD='your_password'")
            print("   - Try with MySQL Workbench first to verify credentials")
        
        return False

if __name__ == "__main__":
    test_mysql_connection()