#!/usr/bin/env python3
"""
SmartGardenHub Quick Setup Script
Automates the complete setup process for the Python Flask conversion
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🌱 SmartGardenHub Python Flask Setup")
    print("=" * 50)
    print("Setting up your educational management system...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_mysql():
    """Check if MySQL is available"""
    print("🗄️  Checking MySQL installation...")
    
    try:
        result = subprocess.run(['mysql', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print("❌ MySQL not found in PATH")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ MySQL not found or not accessible")
        print("   Please install MySQL and ensure it's in your PATH")
        return False

def create_virtual_environment():
    """Create Python virtual environment"""
    print("📦 Creating virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        response = input("   Recreate it? (y/N): ").strip().lower()
        if response == 'y':
            shutil.rmtree(venv_path)
        else:
            print("✅ Using existing virtual environment")
            return True
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_pip_command():
    """Get the correct pip command for the platform"""
    if os.name == 'nt':  # Windows
        return os.path.join('venv', 'Scripts', 'pip.exe')
    else:  # Unix/Linux/macOS
        return os.path.join('venv', 'bin', 'pip')

def get_python_command():
    """Get the correct python command for the platform"""
    if os.name == 'nt':  # Windows
        return os.path.join('venv', 'Scripts', 'python.exe')
    else:  # Unix/Linux/macOS
        return os.path.join('venv', 'bin', 'python')

def install_dependencies():
    """Install Python dependencies"""
    print("📚 Installing Python dependencies...")
    
    pip_cmd = get_pip_command()
    
    try:
        # Upgrade pip first
        subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], check=True)
        
        # Install requirements
        subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("⚙️  Setting up environment configuration...")
    
    env_file = Path('.env')
    example_file = Path('.env.example')
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("   Overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("✅ Using existing .env file")
            return True
    
    if example_file.exists():
        shutil.copy(example_file, env_file)
        print("✅ .env file created from template")
        print("⚠️  Please edit .env file with your actual configuration values")
        return True
    else:
        print("❌ .env.example file not found")
        return False

def setup_database():
    """Setup MySQL database"""
    print("🗄️  Setting up MySQL database...")
    
    python_cmd = get_python_command()
    
    print("\nDatabase setup options:")
    print("1. Create fresh database with sample data")
    print("2. Run migration from PostgreSQL")
    print("3. Skip database setup (manual setup)")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == '1':
        try:
            # Run database migration script
            subprocess.run([python_cmd, 'migrate_database.py'], check=True)
            # Run initialization script
            subprocess.run([python_cmd, 'init_db.py'], check=True)
            print("✅ Database setup completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Database setup failed: {e}")
            return False
    
    elif choice == '2':
        try:
            subprocess.run([python_cmd, 'migrate_database.py'], check=True)
            print("✅ Database migration completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Database migration failed: {e}")
            return False
    
    elif choice == '3':
        print("⚠️  Database setup skipped")
        print("   Run 'python migrate_database.py' manually when ready")
        return True
    
    else:
        print("❌ Invalid choice")
        return False

def create_upload_directory():
    """Create upload directory"""
    print("📁 Creating upload directory...")
    
    upload_dir = Path('static/uploads')
    upload_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Upload directory created")
    return True

def test_application():
    """Test if the application starts correctly"""
    print("🧪 Testing application startup...")
    
    python_cmd = get_python_command()
    
    try:
        # Test import of main modules
        result = subprocess.run([python_cmd, '-c', 'import app; print("Import successful")'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Application modules loaded successfully")
            return True
        else:
            print(f"❌ Application test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Application test timed out")
        return False
    except Exception as e:
        print(f"❌ Application test error: {e}")
        return False

def print_completion_message():
    """Print setup completion message"""
    print("\n🎉 SmartGardenHub Setup Complete!")
    print("=" * 50)
    print()
    print("📝 Next Steps:")
    print("1. Edit .env file with your actual configuration")
    print("2. Ensure MySQL is running and accessible")
    print("3. Configure SMS and AI API keys in .env file")
    print()
    print("🚀 To start the application:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\python.exe app.py")
    else:  # Unix/Linux/macOS
        print("   venv/bin/python app.py")
    
    print()
    print("🌐 Access your application at: http://localhost:5000")
    print()
    print("🔑 Default login credentials (after database setup):")
    print("   Super User: Phone: 01712345678, Password: admin123")
    print("   Teacher:    Phone: 01812345678, Password: teacher123")
    print("   Student:    Phone: 01912345678, Password: student123")
    print()
    print("📚 Documentation: README_PYTHON.md")
    print("🐛 Issues? Check the troubleshooting section in README")

def main():
    """Main setup function"""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_mysql():
        print("⚠️  MySQL check failed, but continuing setup...")
        print("   You can install MySQL later and run database setup manually")
    
    # Setup steps
    steps = [
        ("Create virtual environment", create_virtual_environment),
        ("Install dependencies", install_dependencies),
        ("Create environment file", create_env_file),
        ("Create directories", create_upload_directory),
        ("Test application", test_application),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"\n💥 Setup failed at: {step_name}")
            return False
    
    # Optional database setup
    print(f"\n📋 Database setup...")
    setup_database()  # This can fail but setup continues
    
    print_completion_message()
    return True

if __name__ == '__main__':
    try:
        if main():
            print("\n✨ Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)