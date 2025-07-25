#!/usr/bin/env python3
from app import create_app
from models import db, Book
from utils import normalize_vietnamese_text

app = create_app()
with app.app_context():
    # Test the normalization function
    test_title = "Lãnh đạo bằng câu hỏi"
    normalized = normalize_vietnamese_text(test_title)
    print(f"Original: '{test_title}'")
    print(f"Normalized: '{normalized}'")
    
    # Add a Vietnamese book for testing
    vietnamese_book = Book(
        title="Lãnh đạo bằng câu hỏi", 
        author="Michael J. Marquardt",
        publisher="NXB Tổng hợp TP.HCM",
        language="Vietnamese",
        description="Cuốn sách về nghệ thuật lãnh đạo thông qua việc đặt câu hỏi hiệu quả",
        categories="Lãnh đạo, Quản lý, Kinh doanh",
        copies_total=1,
        copies_available=1
    )
    
    # Update normalized fields
    vietnamese_book.update_normalized_fields()
    
    # Check if book already exists
    existing = Book.query.filter_by(title="Lãnh đạo bằng câu hỏi").first()
    if not existing:
        db.session.add(vietnamese_book)
        db.session.commit()
        print("Added Vietnamese book for testing")
    else:
        print("Vietnamese book already exists")
    
    # Show all books with their normalized fields
    books = Book.query.limit(5).all()
    for book in books:
        print(f"\nBook: {book.title}")
        print(f"  Title normalized: {book.title_normalized}")
        print(f"  Author: {book.author}")
        print(f"  Author normalized: {book.author_normalized}")
