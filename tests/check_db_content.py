#!/usr/bin/env python3
"""
Script to check the database content
"""

import sqlite3
import os

def check_database():
    """Check the database content"""
    
    db_path = os.path.join('instance', 'library.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("LIBRARY DATABASE CONTENT CHECK")
        print("=" * 60)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables in database: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check each table
        for table in tables:
            table_name = table[0]
            print(f"\n📊 Table: {table_name}")
            print("-" * 40)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"   Columns: {[col[1] for col in columns]}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"   Row count: {count}")
            
            # Show first few rows if any exist
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = cursor.fetchall()
                print(f"   Sample data:")
                for i, row in enumerate(rows, 1):
                    print(f"     {i}. {row}")
            else:
                print(f"   ⚠️ No data in this table")
        
        print(f"\n" + "=" * 60)
        print("DATABASE CHECK COMPLETE")
        print("=" * 60)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database()
