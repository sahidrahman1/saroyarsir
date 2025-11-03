"""
WSGI Entry Point for Saro Application
Gunicorn uses this file to start the Flask application
"""
from app import create_app, db

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    # This is used when running directly with python wsgi.py
    # For production, gunicorn will use the 'app' object above
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    app.run(host='0.0.0.0', port=8001, debug=False)
