#!/usr/bin/env python3
"""
Migration script to add thumbnail_url column to books table
"""

import sys
import os

# Add the parent directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Book
from config import Config
from flask import Flask

def migrate_add_thumbnail_url():
    """Add thumbnail_url column to books table"""
    
    # Create Flask app with database configuration
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if column already exists (SQLite method)
            from sqlalchemy import text
            result = db.session.execute(text("PRAGMA table_info(books)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'thumbnail_url' in columns:
                print("thumbnail_url column already exists in books table")
                return
            
            # Add the column
            print("Adding thumbnail_url column to books table...")
            db.session.execute(text("""
                ALTER TABLE books ADD COLUMN thumbnail_url VARCHAR(500)
            """))
            
            db.session.commit()
            print("Successfully added thumbnail_url column to books table")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")
            sys.exit(1)

if __name__ == '__main__':
    print("Starting migration to add thumbnail_url column...")
    migrate_add_thumbnail_url()
    print("Migration completed successfully!")
