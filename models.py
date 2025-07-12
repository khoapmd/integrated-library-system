from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    isbn = db.Column(db.String(20), unique=True, nullable=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(255), nullable=True)
    publication_date = db.Column(db.Date, nullable=True)
    categories = db.Column(db.Text, nullable=True)  # Changed from genre to categories, using Text to store comma-separated values
    description = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(50), nullable=True, default='English')
    pages = db.Column(db.Integer, nullable=True)
    thumbnail_url = db.Column(db.String(500), nullable=True)  # Book cover image URL
    location = db.Column(db.String(100), nullable=True)  # Shelf location
    status = db.Column(db.String(20), nullable=False, default='available')  # available, borrowed, reserved, damaged
    copies_total = db.Column(db.Integer, nullable=False, default=1)
    copies_available = db.Column(db.Integer, nullable=False, default=1)
    added_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='book', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'categories': self.categories,
            'description': self.description,
            'language': self.language,
            'pages': self.pages,
            'thumbnail_url': self.thumbnail_url,
            'location': self.location,
            'status': self.status,
            'copies_total': self.copies_total,
            'copies_available': self.copies_available,
            'added_date': self.added_date.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    membership_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    membership_type = db.Column(db.String(20), nullable=False, default='regular')  # regular, premium, student
    status = db.Column(db.String(20), nullable=False, default='active')  # active, suspended, expired
    max_books = db.Column(db.Integer, nullable=False, default=5)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='member', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'employee_code': self.employee_code,
            'department': self.department,
            'address': self.address,
            'membership_date': self.membership_date.isoformat(),
            'membership_type': self.membership_type,
            'status': self.status,
            'max_books': self.max_books
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # borrow, return, reserve
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)
    fine_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, completed, overdue
    notes = db.Column(db.Text, nullable=True)
    return_condition = db.Column(db.String(20), nullable=True)  # good, fair, damaged, lost
    condition_notes = db.Column(db.Text, nullable=True)
    condition_fee = db.Column(db.Float, nullable=False, default=0.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'member_id': self.member_id,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'fine_amount': self.fine_amount,
            'status': self.status,
            'notes': self.notes,
            'return_condition': self.return_condition,
            'condition_notes': self.condition_notes,
            'condition_fee': self.condition_fee
        }
