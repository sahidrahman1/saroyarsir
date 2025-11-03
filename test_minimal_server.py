#!/usr/bin/env python3
"""
Minimal Flask app to test login
"""
from flask import Flask, request, jsonify, session
from flask_bcrypt import check_password_hash
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from models import db, User, UserRole
from config import config_by_name

app = Flask(__name__)
app.config.from_object(config_by_name['development'])

db.init_app(app)

@app.route('/test-login', methods=['POST'])
def test_login():
    """Minimal login test"""
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        phone = data.get('phoneNumber')
        password = data.get('password')
        
        print(f"Looking for user with phone: {phone}")
        user = User.query.filter_by(phoneNumber=phone).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        print(f"Found user: {user.first_name} {user.last_name}")
        print(f"User role: {user.role.value}")
        
        # Check password
        if user.password_hash and check_password_hash(user.password_hash, password):
            print("Password valid")
            
            # Create minimal response
            response = {
                'success': True,
                'user_role': user.role.value,
                'user_name': f"{user.first_name} {user.last_name}"
            }
            
            return jsonify(response), 200
        else:
            print("Password invalid")
            return jsonify({'error': 'Invalid password'}), 401
            
    except Exception as e:
        print(f"Error in test_login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5002, debug=True)