"""
Updated Configuration for SQLite Development
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    APP_NAME = 'SmartGardenHub'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_THRESHOLD = 500
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'

class DevelopmentConfig(Config):
    """Development configuration with SQLite"""
    DEBUG = True
    
    # SQLite database for development
    base_dir = Path(__file__).parent
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{base_dir}/smartgardenhub.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Use DATABASE_URL from environment, fallback to SQLite
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Use the DATABASE_URL from .env (supports both SQLite and MySQL)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback to SQLite if no DATABASE_URL is set
        base_dir = Path(__file__).parent
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{base_dir}/smartgardenhub.db"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
