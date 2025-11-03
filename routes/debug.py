"""
Debug / Diagnostics Routes
Lightweight endpoints to introspect application state during development.
"""
from flask import Blueprint, jsonify, current_app
import os

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'success': True, 'message': 'pong'})

@debug_bp.route('/env', methods=['GET'])
def environment_info():
    return jsonify({
        'flask_env': os.environ.get('FLASK_ENV'),
        'debug': current_app.debug,
        'config_keys': sorted(list(current_app.config.keys()))[:25]
    })

@debug_bp.route('/blueprints', methods=['GET'])
def list_blueprints():
    return jsonify({'blueprints': list(current_app.blueprints.keys())})