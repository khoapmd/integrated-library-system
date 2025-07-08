import unittest
import json
import tempfile
import os
from app import app, db
from models import Book, Member, Transaction

class LibrarySystemTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            self.create_test_data()
    
    def tearDown(self):
        """Clean up after each test method"""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def create_test_data(self):
        """Create test data"""
        # Create test book
        book = Book(
            isbn='9780134685991',
            title='Test Book',
            author='Test Author',
            publisher='Test Publisher',
            genre='Programming',
            language='English',
            pages=300,
            location='A1-001',
            copies_total=2,
            copies_available=2
        )
        db.session.add(book)
        
        # Create test member
        member = Member(
            member_id='TEST001',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            membership_type='regular'
        )
        db.session.add(member)
        db.session.commit()
    
    def test_get_books(self):
        """Test getting all books"""
        response = self.app.get('/api/books')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('books', data)
        self.assertEqual(len(data['books']), 1)
        self.assertEqual(data['books'][0]['title'], 'Test Book')
    
    def test_add_book(self):
        """Test adding a new book"""
        book_data = {
            'isbn': '9781449331818',
            'title': 'New Test Book',
            'author': 'New Author',
            'publisher': 'New Publisher',
            'genre': 'Technology',
            'language': 'English',
            'pages': 400,
            'location': 'A1-002',
            'copies_total': 1,
            'copies_available': 1
        }
        
        response = self.app.post('/api/books',
                               data=json.dumps(book_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['book']['title'], 'New Test Book')
    
    def test_get_book_by_id(self):
        """Test getting a book by ID"""
        response = self.app.get('/api/books/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Test Book')
    
    def test_get_members(self):
        """Test getting all members"""
        response = self.app.get('/api/members')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['first_name'], 'Test')
    
    def test_add_member(self):
        """Test adding a new member"""
        member_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone': '+1-555-0124',
            'membership_type': 'premium'
        }
        
        response = self.app.post('/api/members',
                               data=json.dumps(member_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['member']['first_name'], 'Jane')
    
    def test_borrow_book(self):
        """Test borrowing a book"""
        borrow_data = {
            'book_id': 1,
            'member_id': 1
        }
        
        response = self.app.post('/api/borrow',
                               data=json.dumps(borrow_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['transaction']['transaction_type'], 'borrow')
    
    def test_isbn_validation(self):
        """Test ISBN validation functionality"""
        from utils import ISBNScanner
        scanner = ISBNScanner()
        
        # Test valid ISBN-13
        self.assertTrue(scanner.is_valid_isbn('9780134685991'))
        
        # Test valid ISBN-10
        self.assertTrue(scanner.is_valid_isbn('0134685997'))
        
        # Test invalid ISBN
        self.assertFalse(scanner.is_valid_isbn('1234567890'))
    
    def test_qr_code_generation(self):
        """Test QR code generation"""
        response = self.app.get('/api/qr/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('qr_code', data)
        self.assertIn('data:image/png;base64,', data['qr_code'])

if __name__ == '__main__':
    unittest.main()
