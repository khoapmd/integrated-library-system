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
            # Check if column already exists
            from sqlalchemy import text
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'books' AND column_name = 'thumbnail_url'
            """))
            
            if result.fetchone():
                print("✅ thumbnail_url column already exists in books table")
                return
            
            # Add the column
            print("📚 Adding thumbnail_url column to books table...")
            db.session.execute(text("""
                ALTER TABLE books ADD COLUMN thumbnail_url VARCHAR(500)
            """))
            
            db.session.commit()
            print("✅ Successfully added thumbnail_url column to books table")
            
            # Optional: Try to populate thumbnail URLs for existing books with ISBNs
            print("🔍 Attempting to populate thumbnail URLs for existing books...")
            
            try:
                from utils import ISBNScanner
                isbn_scanner = ISBNScanner()
                
                books_with_isbn = Book.query.filter(Book.isbn.isnot(None), Book.thumbnail_url.is_(None)).limit(10).all()
                
                updated_count = 0
                for book in books_with_isbn:
                    try:
                        book_info = isbn_scanner.get_book_info_by_isbn(book.isbn)
                        if book_info and book_info.get('cover_url'):
                            book.thumbnail_url = book_info['cover_url']
                            updated_count += 1
                            print(f"  📖 Updated thumbnail for: {book.title}")
                    except Exception as e:
                        print(f"  ❌ Failed to get thumbnail for {book.title}: {e}")
                        continue
                
                if updated_count > 0:
                    db.session.commit()
                    print(f"✅ Updated thumbnail URLs for {updated_count} books")
                else:
                    print("ℹ️  No thumbnail URLs were updated")
                    
            except Exception as e:
                print(f"⚠️  Could not populate thumbnail URLs: {e}")
                print("   (This is optional - thumbnails will be added when books are edited)")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {e}")
            sys.exit(1)

if __name__ == '__main__':
    print("🚀 Starting migration to add thumbnail_url column...")
    migrate_add_thumbnail_url()
    print("🎉 Migration completed successfully!")
