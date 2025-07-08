#!/usr/bin/env python3
"""
Check database schema for members table
"""

import sqlite3
import os

def check_database_schema():
    """Check the current schema of the members table"""
    db_path = os.path.join('instance', 'library.db')
    
    if not os.path.exists(db_path):
        print("Database file not found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(members)")
        columns = cursor.fetchall()
        
        print("Current members table schema:")
        for col in columns:
            nullable = "NOT NULL" if col[3] else ""
            print(f"  {col[1]} {col[2]} {nullable}")
        
        # Check if address column exists
        address_exists = any(col[1] == 'address' for col in columns)
        print(f"\nAddress column exists: {address_exists}")
        
    except Exception as e:
        print(f"Error checking schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database_schema()
