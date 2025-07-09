#!/usr/bin/env python3
"""
Script to test adding sample data to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Book, Member
from datetime import datetime

def test_add_sample_data():
    """Test adding sample data to the database"""
    
    with app.app_context():
        try:
            print("=" * 60)
            print("TESTING DATABASE WRITE OPERATIONS")
            print("=" * 60)
            
            # Test adding a book
            print("\n📚 Testing Book Addition...")
            test_book = Book(
                isbn='9780134685991',
                title='Effective Java',
                author='Joshua Bloch',
                publisher='Addison-Wesley Professional',
                description='A comprehensive guide to best practices in Java programming',
                language='English',
                pages=412,
                location='Programming Section',
                copies_total=2,
                copies_available=2
            )
            
            db.session.add(test_book)
            print(f"   ✅ Book object created: {test_book.title}")
            
            # Test adding a member
            print("\n👤 Testing Member Addition...")
            test_member = Member(
                member_id='LIB001',
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                phone='555-0123',
                employee_code='EMP001',
                department='IT',
                address='123 Main St',
                membership_type='standard'
            )
            
            db.session.add(test_member)
            print(f"   ✅ Member object created: {test_member.first_name} {test_member.last_name}")
            
            # Commit the changes
            print("\n💾 Committing changes to database...")
            db.session.commit()
            print("   ✅ Successfully committed to database")
            
            # Verify the data was saved
            print("\n🔍 Verifying saved data...")
            book_count = Book.query.count()
            member_count = Member.query.count()
            
            print(f"   Books in database: {book_count}")
            print(f"   Members in database: {member_count}")
            
            if book_count > 0:
                saved_book = Book.query.first()
                print(f"   First book: {saved_book.title} by {saved_book.author}")
            
            if member_count > 0:
                saved_member = Member.query.first()
                print(f"   First member: {saved_member.first_name} {saved_member.last_name}")
            
            print(f"\n✅ Test completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_add_sample_data()
