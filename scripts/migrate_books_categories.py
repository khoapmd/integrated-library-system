#!/usr/bin/env python3
"""
Database migration script to rename genre column to categories in books table
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Rename genre column to categories in the books table"""
    db_path = os.path.join('instance', 'library.db')
    
    if not os.path.exists(db_path):
        print("Database file not found. No migration needed.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(books)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        migrations_run = []
        
        if 'genre' in columns and 'categories' not in columns:
            print("Migrating 'genre' column to 'categories'...")
            
            # SQLite doesn't support renaming columns directly in older versions
            # We need to recreate the table
            
            # Get all existing data
            cursor.execute("SELECT * FROM books")
            existing_data = cursor.fetchall()
            
            # Get original column names
            original_columns = [col[1] for col in columns.values()]
            
            # Create new table structure
            cursor.execute("""
                CREATE TABLE books_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn VARCHAR(13) UNIQUE NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    publisher VARCHAR(255),
                    publication_date DATE,
                    categories TEXT,
                    description TEXT,
                    language VARCHAR(50) DEFAULT 'English',
                    pages INTEGER,
                    location VARCHAR(50),
                    copies_total INTEGER DEFAULT 1,
                    copies_available INTEGER DEFAULT 1,
                    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Map data from old table to new table
            if existing_data:
                # Create mapping from old column positions to new column names
                new_columns = ['id', 'isbn', 'title', 'author', 'publisher', 'publication_date', 
                              'categories', 'description', 'language', 'pages', 'location', 
                              'copies_total', 'copies_available', 'date_added', 'last_updated']
                
                # Find the position of 'genre' in original columns
                genre_pos = original_columns.index('genre') if 'genre' in original_columns else None
                
                for row in existing_data:
                    row_list = list(row)
                    # Update the genre data to categories (same position, just renamed)
                    
                    # Create insert statement with proper column mapping
                    placeholders = ', '.join(['?' for _ in new_columns])
                    insert_sql = f"INSERT INTO books_new ({', '.join(new_columns)}) VALUES ({placeholders})"
                    
                    cursor.execute(insert_sql, row_list)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE books")
            cursor.execute("ALTER TABLE books_new RENAME TO books")
            
            migrations_run.append("'genre' column renamed to 'categories'")
            
        elif 'categories' in columns:
            print("'categories' column already exists")
        elif 'genre' not in columns and 'categories' not in columns:
            print("Neither 'genre' nor 'categories' column found - this might be a fresh database")
        
        if migrations_run:
            conn.commit()
            print(f"Migration completed successfully: {', '.join(migrations_run)}")
        else:
            print("No migration needed")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(books)")
        columns_after = cursor.fetchall()
        print("\nTable structure after migration:")
        for col in columns_after:
            print(f"  {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("Starting books table migration...")
    migrate_database()
    print("Migration process completed.")
