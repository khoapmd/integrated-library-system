#!/usr/bin/env python3
"""
Add normalized search columns for Vietnamese accent-insensitive search
This script adds title_normalized and author_normalized columns to enable
bidirectional Vietnamese search (accented finding non-accented and vice versa)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Book
from utils import normalize_vietnamese_text
from sqlalchemy import text

def add_normalized_columns():
    """Add normalized search columns to the books table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist using newer SQLAlchemy syntax
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(books)"))
                columns = [row[1] for row in result]
                
                if 'title_normalized' not in columns:
                    print("Adding title_normalized column...")
                    conn.execute(text("ALTER TABLE books ADD COLUMN title_normalized TEXT"))
                    conn.commit()
                else:
                    print("title_normalized column already exists")
                    
                if 'author_normalized' not in columns:
                    print("Adding author_normalized column...")
                    conn.execute(text("ALTER TABLE books ADD COLUMN author_normalized TEXT"))
                    conn.commit()
                else:
                    print("author_normalized column already exists")
                
                # Create indexes for better search performance
                try:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_book_title_normalized ON books(title_normalized)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_book_author_normalized ON books(author_normalized)"))
                    conn.commit()
                    print("Created search indexes")
                except Exception as e:
                    print(f"Index creation note: {e}")
            
            print("Successfully added normalized columns")
            
        except Exception as e:
            print(f"Error adding columns: {e}")
            db.session.rollback()

def populate_normalized_columns():
    """Populate the normalized columns with existing data"""
    app = create_app()
    
    with app.app_context():
        try:
            books = Book.query.all()
            updated_count = 0
            
            for book in books:
                # Normalize title and author
                if book.title:
                    book.title_normalized = normalize_vietnamese_text(book.title)
                
                if book.author:
                    book.author_normalized = normalize_vietnamese_text(book.author)
                
                updated_count += 1
                
                # Commit in batches for better performance
                if updated_count % 100 == 0:
                    db.session.commit()
                    print(f"Updated {updated_count} books...")
            
            db.session.commit()
            print(f"Successfully normalized {updated_count} books")
            
        except Exception as e:
            print(f"Error populating normalized columns: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("Adding normalized search columns for Vietnamese accent-insensitive search...")
    add_normalized_columns()
    
    print("\nPopulating normalized columns with existing data...")
    populate_normalized_columns()
    
    print("\nMigration completed!")
    print("Vietnamese search now supports accent-insensitive searching.")
    print("Examples:")
    print("- Search 'Lãnh đạo' will find books with 'Lanh dao' in title")
    print("- Search 'lanh dao' will find books with 'Lãnh đạo' in title")
