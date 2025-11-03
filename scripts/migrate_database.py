#!/usr/bin/env python3
"""
Database Migration Script
Converts PostgreSQL data to MySQL format and handles migration
"""
import os
import sys
import json
import subprocess
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_mysql_database():
    """Create MySQL database if it doesn't exist"""
    print("🗄️  Creating MySQL database...")
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        
        cursor = connection.cursor()
        database_name = os.getenv('MYSQL_DATABASE', 'smartgarden_hub')
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{database_name}' created successfully!")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def run_schema_script():
    """Run the MySQL schema creation script"""
    print("🔨 Creating database schema...")
    
    try:
        # Connect to the specific database
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'smartgarden_hub')
        )
        
        cursor = connection.cursor()
        
        # Read and execute schema file
        schema_file = 'mysql_schema.sql'
        if os.path.exists(schema_file):
            with open(schema_file, 'r', encoding='utf-8') as file:
                schema_sql = file.read()
                
                # Split and execute statements
                statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
                
                for statement in statements:
                    if statement:
                        try:
                            cursor.execute(statement)
                        except Error as e:
                            if 'already exists' not in str(e).lower():
                                print(f"⚠️  Warning executing statement: {e}")
                
                connection.commit()
                print("✅ Schema created successfully!")
        else:
            print("❌ Schema file 'mysql_schema.sql' not found")
            return False
            
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Error creating schema: {e}")
        return False

def convert_postgresql_dump_to_mysql(pg_dump_file, mysql_output_file):
    """Convert PostgreSQL dump to MySQL-compatible format"""
    print(f"🔄 Converting PostgreSQL dump to MySQL format...")
    
    if not os.path.exists(pg_dump_file):
        print(f"❌ PostgreSQL dump file '{pg_dump_file}' not found")
        return False
    
    try:
        with open(pg_dump_file, 'r', encoding='utf-8') as pg_file:
            pg_content = pg_file.read()
        
        # PostgreSQL to MySQL conversions
        mysql_content = pg_content
        
        # Convert data types
        mysql_content = mysql_content.replace('SERIAL', 'INT AUTO_INCREMENT')
        mysql_content = mysql_content.replace('BIGSERIAL', 'BIGINT AUTO_INCREMENT')
        mysql_content = mysql_content.replace('BOOLEAN', 'TINYINT(1)')
        mysql_content = mysql_content.replace('TEXT', 'TEXT')
        mysql_content = mysql_content.replace('TIMESTAMP WITH TIME ZONE', 'DATETIME')
        mysql_content = mysql_content.replace('TIMESTAMP WITHOUT TIME ZONE', 'DATETIME')
        mysql_content = mysql_content.replace('NOW()', 'CURRENT_TIMESTAMP')
        
        # Convert PostgreSQL-specific syntax
        mysql_content = mysql_content.replace('NEXTVAL(', 'AUTO_INCREMENT -- NEXTVAL(')
        mysql_content = mysql_content.replace('::text', '')
        mysql_content = mysql_content.replace('::integer', '')
        mysql_content = mysql_content.replace('::boolean', '')
        
        # Convert sequences (not needed in MySQL with AUTO_INCREMENT)
        import re
        mysql_content = re.sub(r'CREATE SEQUENCE.*?;', '', mysql_content, flags=re.MULTILINE | re.DOTALL)
        mysql_content = re.sub(r'ALTER SEQUENCE.*?;', '', mysql_content, flags=re.MULTILINE)
        
        # Convert array types to JSON
        mysql_content = re.sub(r'(\w+)\[\]', r'JSON', mysql_content)
        
        # Convert JSONB to JSON
        mysql_content = mysql_content.replace('JSONB', 'JSON')
        
        # Fix MySQL-specific issues
        mysql_content = mysql_content.replace('SERIAL PRIMARY KEY', 'INT AUTO_INCREMENT PRIMARY KEY')
        
        with open(mysql_output_file, 'w', encoding='utf-8') as mysql_file:
            mysql_file.write(mysql_content)
        
        print(f"✅ Converted dump saved to '{mysql_output_file}'")
        return True
        
    except Exception as e:
        print(f"❌ Error converting dump: {e}")
        return False

def import_mysql_dump(mysql_dump_file):
    """Import MySQL dump file"""
    print(f"📥 Importing data from '{mysql_dump_file}'...")
    
    if not os.path.exists(mysql_dump_file):
        print(f"❌ MySQL dump file '{mysql_dump_file}' not found")
        return False
    
    try:
        mysql_cmd = [
            'mysql',
            f"--host={os.getenv('MYSQL_HOST', 'localhost')}",
            f"--port={os.getenv('MYSQL_PORT', '3306')}",
            f"--user={os.getenv('MYSQL_USER', 'root')}",
            f"--password={os.getenv('MYSQL_PASSWORD', '')}",
            os.getenv('MYSQL_DATABASE', 'smartgarden_hub')
        ]
        
        with open(mysql_dump_file, 'r') as dump_file:
            result = subprocess.run(mysql_cmd, stdin=dump_file, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Data imported successfully!")
            return True
        else:
            print(f"❌ Error importing data: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing dump: {e}")
        return False

def export_postgresql_data():
    """Export data from PostgreSQL using pg_dump"""
    print("📤 Exporting PostgreSQL data...")
    
    pg_host = os.getenv('PG_HOST', 'localhost')
    pg_port = os.getenv('PG_PORT', '5432')
    pg_user = os.getenv('PG_USER', 'postgres')
    pg_database = os.getenv('PG_DATABASE', 'smartgardenhub')
    pg_password = os.getenv('PG_PASSWORD', '')
    
    dump_file = 'postgresql_export.sql'
    
    try:
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        if pg_password:
            env['PGPASSWORD'] = pg_password
        
        pg_dump_cmd = [
            'pg_dump',
            f'--host={pg_host}',
            f'--port={pg_port}',
            f'--username={pg_user}',
            '--data-only',  # Export data only, not schema
            '--inserts',    # Use INSERT statements instead of COPY
            pg_database
        ]
        
        with open(dump_file, 'w') as output_file:
            result = subprocess.run(pg_dump_cmd, stdout=output_file, stderr=subprocess.PIPE, text=True, env=env)
        
        if result.returncode == 0:
            print(f"✅ PostgreSQL data exported to '{dump_file}'")
            return dump_file
        else:
            print(f"❌ Error exporting PostgreSQL data: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error running pg_dump: {e}")
        return None

def test_mysql_connection():
    """Test MySQL connection"""
    print("🔍 Testing MySQL connection...")
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'smartgarden_hub')
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ Connected to MySQL version: {version[0]}")
        
        # Test table count
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📊 Found {len(tables)} tables in database")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 SmartGardenHub Database Migration Tool")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check MySQL connection first
    if not test_mysql_connection():
        print("\n💡 Please check your MySQL configuration in .env file:")
        print("   MYSQL_HOST=localhost")
        print("   MYSQL_PORT=3306")
        print("   MYSQL_USER=your_user")
        print("   MYSQL_PASSWORD=your_password")
        print("   MYSQL_DATABASE=smartgarden_hub")
        return False
    
    print("\nChoose migration option:")
    print("1. Fresh installation (create schema and sample data)")
    print("2. Migrate from PostgreSQL (export + convert + import)")
    print("3. Import existing MySQL dump")
    print("4. Create database and schema only")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        # Fresh installation
        if create_mysql_database() and run_schema_script():
            print("\n🎉 Fresh installation completed successfully!")
            print("\n🔑 You can now run 'python init_db.py' to add sample data")
            return True
    
    elif choice == '2':
        # PostgreSQL migration
        pg_dump = export_postgresql_data()
        if pg_dump:
            mysql_dump = 'mysql_converted_data.sql'
            if convert_postgresql_dump_to_mysql(pg_dump, mysql_dump):
                if create_mysql_database() and run_schema_script():
                    if import_mysql_dump(mysql_dump):
                        print("\n🎉 PostgreSQL migration completed successfully!")
                        return True
    
    elif choice == '3':
        # Import existing MySQL dump
        dump_file = input("Enter path to MySQL dump file: ").strip()
        if create_mysql_database() and import_mysql_dump(dump_file):
            print("\n🎉 MySQL dump imported successfully!")
            return True
    
    elif choice == '4':
        # Create database and schema only
        if create_mysql_database() and run_schema_script():
            print("\n🎉 Database and schema created successfully!")
            return True
    
    else:
        print("❌ Invalid choice!")
        return False
    
    print("\n💥 Migration failed! Please check the error messages above.")
    return False

if __name__ == '__main__':
    if main():
        print("\n✨ Database migration completed successfully!")
        print("🚀 You can now start the application with: python app.py")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)