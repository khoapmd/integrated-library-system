#!/usr/bin/env python3
"""
Database initialization script for PostgreSQL deployment
This script initializes the database with sample data after the PostgreSQL container is ready
"""

import sys
import os
import time

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Book, Member, Transaction
from sqlalchemy import text

def wait_for_db(max_retries=30):
    """Wait for database to be ready"""
    for attempt in range(max_retries):
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
                print("✅ Database connection successful")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⏳ Waiting for database... (attempt {attempt + 1}/{max_retries})")
                print(f"   Error: {e}")
                time.sleep(2)
            else:
                print(f"❌ Failed to connect to database after {max_retries} attempts: {e}")
                return False
    return False

def init_database():
    """Initialize the database with tables and sample data"""
    try:
        with app.app_context():
            # Create all tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created")
            
            # Check if we already have data
            if Book.query.first() is not None:
                print("📚 Database already contains data. Skipping sample data creation.")
                return True
            
            print("📋 Adding sample data...")
            
            # Import and run the existing init_db script
            from scripts.init_db import init_database as run_init
            run_init()
            
            print("✅ Database initialized with sample data")
            return True
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def main():
    """Main function"""
    print("🐘 PostgreSQL Database Initialization")
    print("====================================")
    
    # Wait for database to be ready
    if not wait_for_db():
        sys.exit(1)
    
    # Initialize database
    if not init_database():
        sys.exit(1)
    
    print("🎉 Database initialization complete!")

if __name__ == '__main__':
    main()
