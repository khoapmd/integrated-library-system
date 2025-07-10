#!/usr/bin/env python3
"""
Database migration script to make employee_code required and unique, and email optional
Run this script to update existing database schema and data
"""

import sys
import os

# Add parent directory to Python path to find app module
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from app import app, db
from models import Member
from sqlalchemy import text

def migrate_employee_code():
    """Migrate member data to ensure employee_code is unique and not null, and email is optional"""
    with app.app_context():
        print("🔄 Starting member data migration...")
        print("   - Making employee_code required and unique")
        print("   - Making email optional")
        
        # Check if we're using PostgreSQL or SQLite
        is_postgres = 'postgresql' in str(db.engine.url)
        
        try:
            # Get all members without employee_code
            members_without_code = Member.query.filter(
                (Member.employee_code == None) | 
                (Member.employee_code == '')
            ).all()
            
            print(f"📋 Found {len(members_without_code)} members without employee codes")
            
            # Generate unique employee codes for members that don't have them
            existing_codes = set()
            all_members = Member.query.all()
            
            for member in all_members:
                if member.employee_code and member.employee_code.strip():
                    existing_codes.add(member.employee_code.upper())
            
            counter = 1
            for member in members_without_code:
                # Generate a unique employee code
                while True:
                    new_code = f"EMP{counter:04d}"
                    if new_code not in existing_codes:
                        member.employee_code = new_code
                        existing_codes.add(new_code)
                        print(f"  ✅ Assigned {new_code} to {member.first_name} {member.last_name}")
                        break
                    counter += 1
                counter += 1
            
            # Check for duplicate employee codes among existing members
            codes_seen = set()
            duplicates = []
            
            for member in Member.query.all():
                if member.employee_code:
                    code_upper = member.employee_code.upper()
                    if code_upper in codes_seen:
                        duplicates.append(member)
                    else:
                        codes_seen.add(code_upper)
            
            # Fix duplicate employee codes
            for member in duplicates:
                while True:
                    new_code = f"EMP{counter:04d}"
                    if new_code not in codes_seen:
                        old_code = member.employee_code
                        member.employee_code = new_code
                        codes_seen.add(new_code)
                        print(f"  🔄 Changed duplicate {old_code} to {new_code} for {member.first_name} {member.last_name}")
                        break
                    counter += 1
                counter += 1
            
            # Commit the data changes
            db.session.commit()
            print("✅ Data migration completed")
            
            # Now apply the schema changes
            print("🔧 Applying schema changes...")
            
            if is_postgres:
                # PostgreSQL migration
                try:
                    # First, add the NOT NULL constraint
                    db.session.execute(text("""
                        ALTER TABLE members 
                        ALTER COLUMN employee_code SET NOT NULL;
                    """))
                    print("  ✅ Added NOT NULL constraint")
                    
                    # Then add the unique constraint
                    db.session.execute(text("""
                        ALTER TABLE members 
                        ADD CONSTRAINT unique_employee_code UNIQUE (employee_code);
                    """))
                    print("  ✅ Added UNIQUE constraint for employee_code")
                    
                    # Make email column nullable (optional)
                    db.session.execute(text("""
                        ALTER TABLE members 
                        ALTER COLUMN email DROP NOT NULL;
                    """))
                    print("  ✅ Made email column optional")
                    
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print("  ⚠️  Constraints already exist, skipping...")
                    else:
                        raise e
            else:
                # SQLite migration (recreate table)
                print("  ⚠️  SQLite detected - manual schema update required")
                print("     The model has been updated. Please restart the application")
                print("     to automatically recreate tables with the new schema.")
            
            db.session.commit()
            print("✅ Schema migration completed")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

def main():
    print("🚀 Member Schema Migration Tool")
    print("This will:")
    print("  - Make employee_code required and unique for all members")
    print("  - Make email optional")
    
    with app.app_context():
        # Check current state
        total_members = Member.query.count()
        members_without_code = Member.query.filter(
            (Member.employee_code == None) | 
            (Member.employee_code == '')
        ).count()
        
        print(f"📊 Current state:")
        print(f"   Total members: {total_members}")
        print(f"   Members without employee code: {members_without_code}")
        
        if members_without_code > 0 or total_members > 0:
            response = input(f"\n🤔 Proceed with migration? (y/N): ")
            if response.lower() == 'y':
                migrate_employee_code()
                print("\n🎉 Migration completed successfully!")
                print("   All members now have unique employee codes")
            else:
                print("❌ Migration cancelled")
        else:
            print("✅ No migration needed - database is empty")

if __name__ == '__main__':
    main()
