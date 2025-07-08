#!/usr/bin/env python3
"""
Simple test script to start the Flask server without SSL complications
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

if __name__ == '__main__':
    print("Starting test server...")
    with app.app_context():
        db.create_all()
        print("Database tables created/verified")
    
    print("Starting Flask app on http://localhost:5000")
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
