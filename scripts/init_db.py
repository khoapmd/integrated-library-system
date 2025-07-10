import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Book, Member, Transaction
from datetime import datetime, date

def init_database():
    """Initialize the database with tables and sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we already have data
        if Book.query.first() is not None:
            print("Database already contains data. Skipping sample data creation.")
            return
        
        # Add sample books
        sample_books = [
            {
                'isbn': '9780134685991',
                'title': 'Effective Java',
                'author': 'Joshua Bloch',
                'publisher': 'Addison-Wesley Professional',
                'publication_date': date(2017, 12, 27),
                'categories': 'Programming',
                'description': 'A comprehensive guide to writing effective Java code.',
                'language': 'English',
                'pages': 416,
                'location': 'A1-001',
                'copies_total': 3,
                'copies_available': 3
            },
            {
                'isbn': '9781449331818',
                'title': 'Learning Python',
                'author': 'Mark Lutz',
                'publisher': "O'Reilly Media",
                'publication_date': date(2013, 6, 12),
                'categories': 'Programming',
                'description': 'A comprehensive introduction to Python programming.',
                'language': 'English',
                'pages': 1648,
                'location': 'A1-002',
                'copies_total': 2,
                'copies_available': 2
            },
            {
                'isbn': '9780596517748',
                'title': 'JavaScript: The Good Parts',
                'author': 'Douglas Crockford',
                'publisher': "O'Reilly Media",
                'publication_date': date(2008, 5, 1),
                'categories': 'Programming',
                'description': 'A guide to the best features of JavaScript.',
                'language': 'English',
                'pages': 176,
                'location': 'A1-003',
                'copies_total': 2,
                'copies_available': 2
            },
            {
                'isbn': '9780135957059',
                'title': 'The Pragmatic Programmer',
                'author': 'David Thomas, Andrew Hunt',
                'publisher': 'Addison-Wesley Professional',
                'publication_date': date(2019, 9, 13),
                'categories': 'Programming',
                'description': 'Your journey to mastery, 20th Anniversary Edition.',
                'language': 'English',
                'pages': 352,
                'location': 'A1-004',
                'copies_total': 1,
                'copies_available': 1
            },
            {
                'isbn': '9781617294136',
                'title': 'Clean Code',
                'author': 'Robert C. Martin',
                'publisher': 'Prentice Hall',
                'publication_date': date(2008, 8, 1),
                'categories': 'Programming',
                'description': 'A handbook of agile software craftsmanship.',
                'language': 'English',
                'pages': 464,
                'location': 'A1-005',
                'copies_total': 2,
                'copies_available': 2
            }
        ]
        
        for book_data in sample_books:
            book = Book(**book_data)
            db.session.add(book)
        
        # Add sample members
        sample_members = [
            {
                'member_id': 'LIB001',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@email.com',
                'phone': '+1-555-0123',
                'address': '123 Main St, City, State 12345',
                'membership_type': 'regular',
                'max_books': 5
            },
            {
                'member_id': 'LIB002',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@email.com',
                'phone': '+1-555-0124',
                'address': '456 Oak Ave, City, State 12345',
                'membership_type': 'premium',
                'max_books': 10
            },
            {
                'member_id': 'LIB003',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'email': 'bob.johnson@email.com',
                'phone': '+1-555-0125',
                'address': '789 Pine St, City, State 12345',
                'membership_type': 'student',
                'max_books': 3
            }
        ]
        
        for member_data in sample_members:
            member = Member(**member_data)
            db.session.add(member)
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialized successfully!")
        print(f"Created {len(sample_books)} sample books")
        print(f"Created {len(sample_members)} sample members")

if __name__ == '__main__':
    init_database()
