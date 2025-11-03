#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test if the auth route can be imported
try:
    from routes.auth import auth_bp
    print("✅ Auth route imported successfully")
except Exception as e:
    print(f"❌ Error importing auth route: {e}")
    import traceback
    traceback.print_exc()

# Test if the models work
try:
    from models import User, UserRole
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Error importing models: {e}")
    import traceback
    traceback.print_exc()

print("Test completed!")