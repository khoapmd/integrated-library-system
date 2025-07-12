#!/usr/bin/env python3
"""
Database migration script for adding thumbnail_url column
Works with both SQLite (development) and PostgreSQL (production)
"""

import sys
import os

# Add the parent directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Book
from config import Config
from flask import Flask
import logging

def detect_database_type():
    """Detect if we're using SQLite or PostgreSQL"""
    config = Config()
    database_url = config.SQLALCHEMY_DATABASE_URI
    
    if database_url.startswith('sqlite'):
        return 'sqlite'
    elif database_url.startswith('postgresql'):
        return 'postgresql'
    else:
        return 'unknown'

def column_exists(table_name, column_name, db_type):
    """Check if a column exists in the table"""
    from sqlalchemy import text
    
    if db_type == 'sqlite':
        result = db.session.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result.fetchall()]
        return column_name in columns
    elif db_type == 'postgresql':
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table_name AND column_name = :column_name
        """), {'table_name': table_name, 'column_name': column_name})
        return result.fetchone() is not None
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def add_thumbnail_url_column():
    """Add thumbnail_url column to books table"""
    
    # Create Flask app with database configuration
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Detect database type
            db_type = detect_database_type()
            print(f"🔍 Detected database type: {db_type}")
            
            # Check if column already exists
            if column_exists('books', 'thumbnail_url', db_type):
                print("✅ thumbnail_url column already exists in books table")
                return True
            
            # Add the column
            print("📚 Adding thumbnail_url column to books table...")
            from sqlalchemy import text
            
            if db_type == 'sqlite':
                db.session.execute(text("ALTER TABLE books ADD COLUMN thumbnail_url VARCHAR(500)"))
            elif db_type == 'postgresql':
                db.session.execute(text("ALTER TABLE books ADD COLUMN thumbnail_url VARCHAR(500)"))
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            db.session.commit()
            print("✅ Successfully added thumbnail_url column to books table")
            
            # Optional: Try to populate thumbnail URLs for existing books with ISBNs
            try:
                print("🔍 Checking for books that need thumbnail URLs...")
                from utils import ISBNScanner
                isbn_scanner = ISBNScanner()
                
                # Get a few books with ISBNs but no thumbnails
                books_with_isbn = Book.query.filter(
                    Book.isbn.isnot(None), 
                    Book.thumbnail_url.is_(None)
                ).limit(5).all()
                
                updated_count = 0
                for book in books_with_isbn:
                    try:
                        print(f"  📖 Looking up thumbnail for: {book.title}")
                        book_info = isbn_scanner.get_book_info_by_isbn(book.isbn)
                        if book_info and book_info.get('cover_url'):
                            book.thumbnail_url = book_info['cover_url']
                            updated_count += 1
                            print(f"    ✅ Updated thumbnail URL")
                        else:
                            print(f"    ⚠️  No thumbnail found")
                    except Exception as e:
                        print(f"    ❌ Failed to get thumbnail: {e}")
                        continue
                
                if updated_count > 0:
                    db.session.commit()
                    print(f"✅ Updated thumbnail URLs for {updated_count} books")
                else:
                    print("ℹ️  No thumbnail URLs were updated")
                    
            except Exception as e:
                print(f"⚠️  Could not populate thumbnail URLs: {e}")
                print("   (This is optional - thumbnails will be added when books are edited)")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {e}")
            return False

def main():
    print("🚀 Starting database migration: Add thumbnail_url column")
    print("=" * 50)
    
    success = add_thumbnail_url_column()
    
    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
