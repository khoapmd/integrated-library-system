#!/usr/bin/env python3
"""
Database migration script to add employee_code and department columns to members table
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add employee_code and department columns to the members table"""
    db_path = os.path.join('instance', 'library.db')
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the app first to create the database.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(members)")
        columns = [col[1] for col in cursor.fetchall()]
        
        migrations_run = []
        
        if 'employee_code' not in columns:
            print("Adding employee_code column...")
            cursor.execute("ALTER TABLE members ADD COLUMN employee_code VARCHAR(20)")
            migrations_run.append("employee_code column added")
        else:
            print("employee_code column already exists")
        
        if 'department' not in columns:
            print("Adding department column...")
            cursor.execute("ALTER TABLE members ADD COLUMN department VARCHAR(50)")
            migrations_run.append("department column added")
        else:
            print("department column already exists")
        
        if migrations_run:
            conn.commit()
            print(f"Migration completed successfully: {', '.join(migrations_run)}")
        else:
            print("No migration needed - all columns already exist")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(members)")
        columns = cursor.fetchall()
        print("\nCurrent members table schema:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
