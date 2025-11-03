"""
User Management Routes (Legacy placeholder)
Provides minimal endpoints to satisfy tests expecting users blueprint.
In current codebase student-specific operations moved to students blueprint.
"""
from flask import Blueprint, jsonify

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
def list_users():
	"""Return a basic users list placeholder.
	This can be expanded or deprecated; kept for backward compatibility with tests.
	"""
	return jsonify({
		'success': True,
		'message': 'Users endpoint placeholder',
		'data': []
	})

@users_bp.route('/health', methods=['GET'])
def users_health():
	return jsonify({'status': 'ok', 'component': 'users'})