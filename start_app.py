"""
Simple Flask App Launcher
Fix network binding issues
"""
import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from app import create_app
    
    print("🚀 Starting SmartGardenHub...")
    app = create_app()
    
    # Use localhost binding for better compatibility
    HOST = '127.0.0.1'
    PORT = 5000
    
    print(f"📍 Server will be available at: http://{HOST}:{PORT}")
    print("🔐 Login with:")
    print("   Teacher: 01812345678 / teacher123")
    print("   Student: 01912345678 / student123")
    print("   Admin: 01712345678 / admin123")
    print("=" * 50)
    
    app.run(
        host=HOST,
        port=PORT,
        debug=True,
        use_reloader=False,  # Disable reloader to avoid port conflicts
        threaded=True
    )
    
except Exception as e:
    print(f"❌ Error starting Flask app: {e}")
    print("💡 Make sure you're in the python_conversion directory")
    sys.exit(1)