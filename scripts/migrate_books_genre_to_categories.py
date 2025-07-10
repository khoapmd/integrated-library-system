#!/usr/bin/env python3
"""
Migration script to rename 'genre' column to 'categories' in books table
"""

import sqlite3
import os
import sys

# Add the parent directory to the path so we can import from the project
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def migrate_books_table():
    """Migrate the books table from genre to categories column"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'library.db')
    
    print(f"Starting books table migration...")
    print(f"Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(books)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns: {column_names}")
        
        if 'categories' in column_names and 'genre' not in column_names:
            print("Migration already completed - 'categories' column exists and 'genre' does not.")
            conn.close()
            return True
        
        if 'genre' not in column_names:
            print("Error: 'genre' column not found in books table.")
            conn.close()
            return False
        
        print("Migrating 'genre' column to 'categories'...")
        
        # Step 1: Create a new table with the correct schema
        cursor.execute('''
            CREATE TABLE books_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid VARCHAR(36) UNIQUE NOT NULL,
                isbn VARCHAR(20),
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                publisher VARCHAR(255),
                publication_date DATE,
                categories VARCHAR(100),
                description TEXT,
                language VARCHAR(50) DEFAULT 'English',
                pages INTEGER,
                location VARCHAR(100),
                status VARCHAR(20) DEFAULT 'available',
                copies_total INTEGER DEFAULT 1,
                copies_available INTEGER DEFAULT 1,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Step 2: Copy data from old table to new table
        cursor.execute('''
            INSERT INTO books_new (
                id, uuid, isbn, title, author, publisher, publication_date, 
                categories, description, language, pages, location, status, 
                copies_total, copies_available, added_date, last_updated
            )
            SELECT 
                id, uuid, isbn, title, author, publisher, publication_date, 
                genre, description, language, pages, location, status, 
                copies_total, copies_available, added_date, last_updated
            FROM books
        ''')
        
        # Step 3: Drop the old table
        cursor.execute('DROP TABLE books')
        
        # Step 4: Rename the new table
        cursor.execute('ALTER TABLE books_new RENAME TO books')
        
        # Commit the changes
        conn.commit()
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(books)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        
        print(f"New columns: {new_column_names}")
        
        if 'categories' in new_column_names and 'genre' not in new_column_names:
            print("✅ Migration completed successfully!")
            
            # Check how many records were migrated
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            print(f"✅ Migrated {count} book records")
            
            conn.close()
            return True
        else:
            print("❌ Migration verification failed")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

if __name__ == "__main__":
    success = migrate_books_table()
    if success:
        print("Migration process completed successfully.")
        sys.exit(0)
    else:
        print("Migration process failed.")
        sys.exit(1)
