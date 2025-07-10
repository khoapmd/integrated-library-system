from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db, Book, Member, Transaction
from utils import QRCodeManager, ISBNScanner, generate_member_id, calculate_fine
from config import config, Config
import os
import io
from datetime import datetime, timedelta
import json

# Create Flask app with proper configuration
def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Configure for reverse proxy (Cloudflare tunnel, nginx, etc.)
    # This middleware handles X-Forwarded-For, X-Forwarded-Proto, etc.
    if not app.debug:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    return app

# Create app instance
app = create_app(os.environ.get('FLASK_ENV', 'default'))

# Initialize utilities
qr_manager = QRCodeManager()
isbn_scanner = ISBNScanner()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books')
def books_page():
    return render_template('books.html')

@app.route('/scanner')
def scanner_page():
    return render_template('scanner.html')

@app.route('/debug-scanner')
def debug_scanner():
    """Debug page for testing scanner functionality"""
    return render_template('debug_scanner.html')

@app.route('/test-scanner')
def test_scanner_page():
    # Redirect to system test page since scanner tests are now consolidated there
    return redirect(url_for('system_test'))

@app.route('/circulation')
def circulation_page():
    return render_template('circulation.html')

@app.route('/members')
def members_page():
    return render_template('members.html')

@app.route('/system-test')
def system_test_page():
    return render_template('system_test.html')

@app.route('/qr-generator')
def qr_generator():
    """QR code generator for testing circulation scanner"""
    return render_template('qr_generator.html')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_file('static/img/logo.svg', mimetype='image/svg+xml')

@app.route('/test-member-qr')
def test_member_qr():
    """Redirect to system test page where all tests are consolidated"""
    from flask import redirect, url_for
    return redirect(url_for('system_test_page'))

@app.route('/health')
def health_check():
    """Health check endpoint for Docker and monitoring"""
    try:
        # Check database connectivity
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'error',
            'error': str(e)
        }), 503

@app.route('/ready')
def readiness_check():
    """Readiness check for Kubernetes/orchestration"""
    try:
        # More comprehensive checks can be added here
        book_count = Book.query.count()
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.now().isoformat(),
            'database': 'ready',
            'books_count': book_count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503

# API Routes

@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books with pagination and search"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    query = Book.query
    
    if search:
        query = query.filter(
            (Book.title.contains(search)) |
            (Book.author.contains(search)) |
            (Book.isbn.contains(search))
        )
    
    books = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'books': [book.to_dict() for book in books.items],
        'total': books.total,
        'pages': books.pages,
        'current_page': page
    })

@app.route('/api/books', methods=['POST'])
def add_book():
    """Add a new book or add copies to existing book"""
    data = request.get_json()
    
    try:
        isbn = data.get('isbn')
        
        # Check if book already exists by ISBN
        existing_book = None
        if isbn:
            existing_book = Book.query.filter_by(isbn=isbn).first()
        
        if existing_book:
            # Book exists, add more copies
            copies_to_add = data.get('copies_total', 1)
            available_to_add = data.get('copies_available', 1)
            
            existing_book.copies_total += copies_to_add
            existing_book.copies_available += available_to_add
            existing_book.last_updated = datetime.utcnow()
            
            # Update other fields if they were provided
            if data.get('location') and not existing_book.location:
                existing_book.location = data.get('location')
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'book': existing_book.to_dict(),
                'message': f'Added {copies_to_add} more copies to existing book. Total copies: {existing_book.copies_total}',
                'action': 'updated_existing'
            }), 200
        else:
            # Create new book
            book = Book(
                isbn=isbn,
                title=data['title'],
                author=data['author'],
                publisher=data.get('publisher'),
                categories=data.get('categories'),
                description=data.get('description'),
                language=data.get('language', 'English'),
                pages=data.get('pages'),
                location=data.get('location'),
                copies_total=data.get('copies_total', 1),
                copies_available=data.get('copies_available', 1)
            )
            
            db.session.add(book)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'book': book.to_dict(),
                'message': 'New book added successfully',
                'action': 'created_new'
            }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error adding book: {str(e)}'
        }), 400

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book"""
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update a book"""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    try:
        for key, value in data.items():
            if hasattr(book, key) and key != 'id':
                setattr(book, key, value)
        
        book.last_updated = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'book': book.to_dict(),
            'message': 'Book updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating book: {str(e)}'
        }), 400

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    book = Book.query.get_or_404(book_id)
    
    try:
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Book deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting book: {str(e)}'
        }), 400

@app.route('/api/books/isbn/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    """Get book information by ISBN from library database"""
    try:
        book = Book.query.filter_by(isbn=isbn).first()
        if book:
            return jsonify({
                'success': True,
                'book': book.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Book not found in library'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving book: {str(e)}'
        }), 400

@app.route('/api/books/uuid/<uuid>', methods=['GET'])
def get_book_by_uuid(uuid):
    """Get book information by UUID from library database"""
    try:
        book = Book.query.filter_by(uuid=uuid).first()
        if book:
            return jsonify({
                'success': True,
                'book': book.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Book not found in library'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving book: {str(e)}'
        }), 400

@app.route('/api/isbn/lookup/<isbn>', methods=['GET'])
def lookup_isbn_external(isbn):
    """Get book information by ISBN from Google Books API"""
    try:
        # Clean the ISBN
        import isbnlib
        clean_isbn = isbnlib.clean(isbn)
        
        if not (isbnlib.is_isbn10(clean_isbn) or isbnlib.is_isbn13(clean_isbn)):
            return jsonify({
                'success': False,
                'message': 'Invalid ISBN format'
            }), 400
        
        # Get book info from Google Books API
        book_info = isbn_scanner.get_book_info_by_isbn(clean_isbn)
        
        if book_info:
            # Check how many copies we already have in the database
            existing_book = Book.query.filter_by(isbn=clean_isbn).first()
            suggested_copies = 1 if not existing_book else existing_book.copies_total + 1
            
            # Add suggested copy count to the response
            book_info['suggested_copies'] = suggested_copies
            book_info['existing_in_library'] = existing_book is not None
            
            if existing_book:
                book_info['existing_book'] = existing_book.to_dict()
            
            return jsonify({
                'success': True,
                'book_info': book_info
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Book information not found for this ISBN'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error looking up ISBN: {str(e)}'
        }), 400

# QR Code Routes

@app.route('/api/qr/<int:book_id>', methods=['GET'])
def generate_qr_code(book_id):
    """Generate QR code for a book"""
    book = Book.query.get_or_404(book_id)
    
    try:
        qr_code_data = qr_manager.generate_qr_code(book.uuid)
        return jsonify({
            'success': True,
            'qr_code': qr_code_data,
            'book': book.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating QR code: {str(e)}'
        }), 400

@app.route('/api/scan/qr', methods=['POST'])
def scan_qr_code():
    """Scan QR code from uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No image file provided'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No image file selected'
            }), 400
        
        # Read image data
        image_data = file.read()
        
        # Scan QR code
        qr_results = qr_manager.scan_qr_code(image_data)
        
        if qr_results:
            books = []
            members = []
            for qr_result in qr_results:
                if 'uuid' in qr_result:
                    # Look up book by UUID
                    book = Book.query.filter_by(uuid=qr_result['uuid']).first()
                    if book:
                        books.append(book.to_dict())
                elif 'employee_code' in qr_result:
                    # Look up member by employee code
                    member = Member.query.filter_by(employee_code=qr_result['employee_code']).first()
                    if member:
                        members.append(member.to_dict())
            
            return jsonify({
                'success': True,
                'qr_results': qr_results,
                'books': books,
                'members': members
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No QR codes found in image'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error scanning QR code: {str(e)}'
        }), 400

@app.route('/api/scan/member-qr', methods=['POST'])
def scan_member_qr_code():
    """Scan member QR code from uploaded image or data"""
    try:
        data = request.get_json()
        
        if not data or 'qr_data' not in data:
            return jsonify({
                'success': False,
                'message': 'No QR data provided'
            }), 400
        
        qr_data = data['qr_data']
        
        # Try to parse as JSON first (for library member cards)
        try:
            parsed_data = json.loads(qr_data)
            if parsed_data.get('type') == 'library_member':
                employee_code = parsed_data.get('employee_code')
                if employee_code:
                    member = Member.query.filter_by(employee_code=employee_code).first()
                    if member:
                        return jsonify({
                            'success': True,
                            'member': member.to_dict(),
                            'qr_type': 'library_member'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'message': f'No member found with employee code: {employee_code}'
                        }), 404
        except json.JSONDecodeError:
            pass
        
        # Try direct employee code lookup
        member = Member.query.filter_by(employee_code=qr_data).first()
        if member:
            return jsonify({
                'success': True,
                'member': member.to_dict(),
                'qr_type': 'employee_code'
            })
        
        # Try member ID lookup
        member = Member.query.filter_by(member_id=qr_data).first()
        if member:
            return jsonify({
                'success': True,
                'member': member.to_dict(),
                'qr_type': 'member_id'
            })
        
        return jsonify({
            'success': False,
            'message': 'No member found for the scanned QR code'
        }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error scanning member QR code: {str(e)}'
        }), 400

# Circulation Management Endpoints
@app.route('/api/circulation/checkout', methods=['POST'])
def checkout_book():
    """Check out a book using QR code scan"""
    try:
        data = request.get_json()
        book_uuid = data.get('book_uuid')
        member_id = data.get('member_id')
        due_days = data.get('due_days', 14)  # Default 14 days
        
        if not book_uuid or not member_id:
            return jsonify({
                'success': False,
                'message': 'Book UUID and Member ID are required'
            }), 400
        
        # Find the book
        book = Book.query.filter_by(uuid=book_uuid).first()
        if not book:
            return jsonify({
                'success': False,
                'message': 'Book not found'
            }), 404
        
        # Check if book is available
        if book.copies_available <= 0:
            return jsonify({
                'success': False,
                'message': 'No copies available for checkout'
            }), 400
        
        # Find the member
        member = Member.query.get(member_id)
        if not member:
            return jsonify({
                'success': False,
                'message': 'Member not found'
            }), 404
        
        # Check if member has reached borrowing limit
        active_loans = Transaction.query.filter_by(
            member_id=member_id,
            transaction_type='borrow',
            status='active'
        ).count()
        
        if active_loans >= member.max_books:
            return jsonify({
                'success': False,
                'message': f'Member has reached maximum borrowing limit ({member.max_books} books)'
            }), 400
        
        # Create checkout transaction
        due_date = datetime.utcnow() + timedelta(days=due_days)
        transaction = Transaction(
            book_id=book.id,
            member_id=member.id,
            transaction_type='borrow',
            due_date=due_date,
            status='active'
        )
        
        # Update book availability
        book.copies_available -= 1
        if book.copies_available == 0:
            book.status = 'borrowed'
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Book checked out successfully',
            'transaction': transaction.to_dict(),
            'book': book.to_dict(),
            'member': member.to_dict(),
            'due_date': due_date.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error during checkout: {str(e)}'
        }), 400

@app.route('/api/circulation/checkin', methods=['POST'])
def checkin_book():
    """Check in a book using QR code scan"""
    try:
        data = request.get_json()
        book_uuid = data.get('book_uuid')
        member_id = data.get('member_id')
        condition = data.get('condition', 'good')
        condition_notes = data.get('condition_notes', '')
        condition_fee = data.get('condition_fee', 0.0)
        
        if not book_uuid:
            return jsonify({
                'success': False,
                'message': 'Book UUID is required'
            }), 400
        
        # Validate condition
        valid_conditions = ['good', 'fair', 'damaged', 'lost']
        if condition not in valid_conditions:
            return jsonify({
                'success': False,
                'message': 'Invalid book condition'
            }), 400
        
        # Validate condition fee
        try:
            condition_fee = float(condition_fee)
            if condition_fee < 0:
                return jsonify({
                    'success': False,
                    'message': 'Condition fee cannot be negative'
                }), 400
        except (ValueError, TypeError):
            condition_fee = 0.0
        
        # Find the book
        book = Book.query.filter_by(uuid=book_uuid).first()
        if not book:
            return jsonify({
                'success': False,
                'message': 'Book not found'
            }), 404
        
        # Find active transaction for this book
        transaction_query = Transaction.query.filter_by(
            book_id=book.id,
            transaction_type='borrow',
            status='active'
        )
        
        if member_id:
            transaction_query = transaction_query.filter_by(member_id=member_id)
        
        transaction = transaction_query.first()
        
        if not transaction:
            return jsonify({
                'success': False,
                'message': 'No active checkout found for this book' + (f' and member' if member_id else '')
            }), 404
        
        # Calculate fine if overdue
        return_date = datetime.utcnow()
        fine_amount = 0.0
        
        if return_date > transaction.due_date:
            days_overdue = (return_date - transaction.due_date).days
            fine_amount = calculate_fine(transaction.due_date, return_date)
        
        # Use custom condition fee if provided, otherwise use default fees
        if condition_fee == 0.0:  # Only apply default if no custom fee was provided
            if condition == 'damaged':
                condition_fee = 15.0  # $15 default damage fee
            elif condition == 'lost':
                condition_fee = 50.0  # $50 default replacement fee
        
        # Update transaction
        transaction.return_date = return_date
        transaction.fine_amount = fine_amount
        transaction.condition_fee = condition_fee
        transaction.return_condition = condition
        transaction.condition_notes = condition_notes
        transaction.status = 'completed'
        
        # Update book availability and status
        book.copies_available += 1
        if book.copies_available > 0 and condition in ['good', 'fair']:
            book.status = 'available'
        elif condition in ['damaged', 'lost']:
            # For damaged/lost books, don't make them available
            book.copies_available -= 1
            if condition == 'lost':
                book.copies_total -= 1  # Remove lost books from total count
        
        db.session.commit()
        
        member = Member.query.get(transaction.member_id)
        
        return jsonify({
            'success': True,
            'message': 'Book checked in successfully',
            'transaction': transaction.to_dict(),
            'book': book.to_dict(),
            'member': member.to_dict() if member else None,
            'fine_amount': fine_amount,
            'condition_fee': condition_fee,
            'was_overdue': fine_amount > 0,
            'condition': condition,
            'condition_notes': condition_notes
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error during checkin: {str(e)}'
        }), 400

@app.route('/api/circulation/status/<book_uuid>')
def get_circulation_status(book_uuid):
    """Get circulation status of a book"""
    try:
        book = Book.query.filter_by(uuid=book_uuid).first()
        if not book:
            return jsonify({
                'success': False,
                'message': 'Book not found'
            }), 404
        
        # Get active transactions
        active_transactions = Transaction.query.filter_by(
            book_id=book.id,
            transaction_type='borrow',
            status='active'
        ).all()
        
        transactions_data = []
        for trans in active_transactions:
            member = Member.query.get(trans.member_id)
            trans_dict = trans.to_dict()
            trans_dict['member'] = member.to_dict() if member else None
            trans_dict['is_overdue'] = datetime.utcnow() > trans.due_date
            transactions_data.append(trans_dict)
        
        return jsonify({
            'success': True,
            'book': book.to_dict(),
            'active_transactions': transactions_data,
            'is_available': book.copies_available > 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting circulation status: {str(e)}'
        }), 400

# Member Management Endpoints
@app.route('/api/members', methods=['GET'])
def get_members():
    """Get all members"""
    try:
        members = Member.query.all()
        return jsonify({
            'success': True,
            'members': [member.to_dict() for member in members],
            'total': len(members)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving members: {str(e)}'
        }), 400

@app.route('/api/members', methods=['POST'])
def add_member():
    """Add a new member"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'employee_code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        # Check if employee_code already exists
        existing_member = Member.query.filter_by(employee_code=data['employee_code']).first()
        if existing_member:
            return jsonify({
                'success': False,
                'message': 'Employee code already exists'
            }), 400
        
        # Check if email already exists (only if email is provided)
        if data.get('email'):
            existing_email = Member.query.filter_by(email=data['email']).first()
            if existing_email:
                return jsonify({
                    'success': False,
                    'message': 'Email already exists'
                }), 400
        
        member = Member(
            member_id=generate_member_id(),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            employee_code=data['employee_code'],
            department=data.get('department'),
            membership_type=data.get('membership_type', 'regular'),
            max_books=data.get('max_books', 5)
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'member': member.to_dict(),
            'message': 'Member added successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error adding member: {str(e)}'
        }), 400

@app.route('/api/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    """Update an existing member"""
    try:
        member = db.session.get(Member, member_id)
        if not member:
            return jsonify({
                'success': False,
                'message': 'Member not found'
            }), 404
        
        data = request.get_json()
        
        # Check if employee_code is being updated and if it already exists
        if 'employee_code' in data and data['employee_code'] != member.employee_code:
            if not data['employee_code']:
                return jsonify({
                    'success': False,
                    'message': 'Employee code is required'
                }), 400
                
            existing_member = Member.query.filter_by(employee_code=data['employee_code']).first()
            if existing_member:
                return jsonify({
                    'success': False,
                    'message': 'Employee code already exists'
                }), 400
        
        # Check if email is being updated and if it already exists
        if 'email' in data and data['email'] and data['email'] != member.email:
            existing_email = Member.query.filter_by(email=data['email']).first()
            if existing_email:
                return jsonify({
                    'success': False,
                    'message': 'Email already exists'
                }), 400
        
        # Update member fields
        member.first_name = data.get('first_name', member.first_name)
        member.last_name = data.get('last_name', member.last_name)
        member.email = data.get('email', member.email)
        member.phone = data.get('phone', member.phone)
        member.employee_code = data.get('employee_code', member.employee_code)
        member.department = data.get('department', member.department)
        member.membership_type = data.get('membership_type', member.membership_type)
        member.max_books = data.get('max_books', member.max_books)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'member': member.to_dict(),
            'message': 'Member updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating member: {str(e)}'
        }), 400

@app.route('/api/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    """Get a specific member by ID"""
    try:
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({
                'success': False,
                'message': 'Member not found'
            }), 404
        
        return jsonify({
            'success': True,
            'member': member.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching member: {str(e)}'
        }), 500

@app.route('/api/members/employee/<employee_code>', methods=['GET'])
def get_member_by_employee_code(employee_code):
    """Get a member by employee code"""
    try:
        member = Member.query.filter_by(employee_code=employee_code).first()
        
        if not member:
            return jsonify({
                'success': False,
                'message': f'No member found with employee code: {employee_code}'
            }), 404
        
        return jsonify({
            'success': True,
            'member': member.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching member: {str(e)}'
        }), 500

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """Delete a member by ID"""
    try:
        member = db.session.get(Member, member_id)
        if not member:
            return jsonify({
                'success': False,
                'message': 'Member not found'
            }), 404
        
        # Check if member has active transactions
        active_transactions = Transaction.query.filter_by(
            member_id=member_id,
            status='active'
        ).first()
        
        if active_transactions:
            return jsonify({
                'success': False,
                'message': 'Cannot delete member with active book loans. Please return all books first.'
            }), 400
        
        # Delete the member
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Member deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting member: {str(e)}'
        }), 400

# Transaction Routes

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions"""
    transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).all()
    return jsonify([trans.to_dict() for trans in transactions])

@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    """Borrow a book"""
    data = request.get_json()
    book_id = data['book_id']
    member_id = data['member_id']
    
    book = Book.query.get_or_404(book_id)
    member = Member.query.get_or_404(member_id)
    
    if book.copies_available <= 0:
        return jsonify({
            'success': False,
            'message': 'No copies available'
        }), 400
    
    try:
        # Create transaction
        transaction = Transaction(
            book_id=book_id,
            member_id=member_id,
            transaction_type='borrow',
            due_date=datetime.utcnow() + timedelta(days=14)  # 2 weeks loan period
        )
        
        # Update book availability
        book.copies_available -= 1
        if book.copies_available == 0:
            book.status = 'borrowed'
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict(),
            'message': 'Book borrowed successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error borrowing book: {str(e)}'
        }), 400

@app.route('/api/return', methods=['POST'])
def return_book():
    """Return a book"""
    data = request.get_json()
    transaction_id = data['transaction_id']
    
    transaction = Transaction.query.get_or_404(transaction_id)
    book = Book.query.get(transaction.book_id)
    
    try:
        # Update transaction
        transaction.return_date = datetime.utcnow()
        transaction.status = 'completed'
        
        # Calculate fine if overdue
        if transaction.return_date > transaction.due_date:
            days_overdue = (transaction.return_date - transaction.due_date).days
            transaction.fine_amount = days_overdue * 1.0  # $1 per day
        
        # Update book availability
        book.copies_available += 1
        if book.copies_available > 0:
            book.status = 'available'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict(),
            'fine_amount': transaction.fine_amount,
            'message': 'Book returned successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error returning book: {str(e)}'
        }), 400

@app.route('/api/qr/generate/<book_uuid>')
def generate_qr_code_by_uuid(book_uuid):
    """Generate QR code for a book by UUID"""
    try:
        book = Book.query.filter_by(uuid=book_uuid).first()
        if not book:
            return jsonify({
                'success': False,
                'message': 'Book not found'
            }), 404
        
        # Generate QR code
        qr_code_data = qr_manager.generate_qr_code(book_uuid)
        
        return jsonify({
            'success': True,
            'qr_code': qr_code_data,
            'book': book.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating QR code: {str(e)}'
        }), 400

@app.route('/api/test/qr/<book_uuid>')
def test_qr_page(book_uuid):
    """Test page to display a QR code for scanning"""
    try:
        book = Book.query.filter_by(uuid=book_uuid).first()
        if not book:
            return f"Book with UUID {book_uuid} not found", 404
        
        qr_code_data = qr_manager.generate_qr_code(book_uuid)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test QR Code - {book.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .qr-container {{ margin: 20px auto; max-width: 400px; }}
                .book-info {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px auto; max-width: 500px; }}
            </style>
        </head>
        <body>
            <h1>Test QR Code</h1>
            <div class="book-info">
                <h2>{book.title}</h2>
                <p><strong>Author:</strong> {book.author}</p>
                <p><strong>ISBN:</strong> {book.isbn}</p>
                <p><strong>UUID:</strong> {book.uuid}</p>
            </div>
            <div class="qr-container">
                <h3>QR Code for Scanning:</h3>
                <img src="{qr_code_data}" alt="QR Code" style="max-width: 300px;">
            </div>
            <p><a href="/scanner">Go to Scanner</a></p>
        </body>
        </html>
        """
        return html
        
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/api/circulation/recent')
def get_recent_transactions():
    """Get recent circulation transactions"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get recent transactions (both checkout and checkin)
        recent_transactions = Transaction.query.filter(
            Transaction.transaction_type == 'borrow'
        ).order_by(
            Transaction.transaction_date.desc()
        ).limit(limit).all()
        
        transactions_data = []
        for trans in recent_transactions:
            # Get related data
            book = Book.query.get(trans.book_id)
            member = Member.query.get(trans.member_id)
            
            trans_dict = trans.to_dict()
            trans_dict['book'] = book.to_dict() if book else None
            trans_dict['member'] = member.to_dict() if member else None
            
            # Add display information
            trans_dict['is_overdue'] = False
            trans_dict['is_completed'] = trans.status == 'completed'
            
            if trans.status == 'active' and trans.due_date:
                trans_dict['is_overdue'] = datetime.utcnow() > trans.due_date
                trans_dict['days_until_due'] = (trans.due_date - datetime.utcnow()).days
            
            # Add human-readable transaction type
            if trans.status == 'completed' and trans.return_date:
                trans_dict['display_type'] = 'Check-in'
                trans_dict['display_date'] = trans.return_date
            else:
                trans_dict['display_type'] = 'Check-out'
                trans_dict['display_date'] = trans.transaction_date
            
            transactions_data.append(trans_dict)
        
        return jsonify({
            'success': True,
            'transactions': transactions_data,
            'count': len(transactions_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching recent transactions: {str(e)}'
        }), 400

if __name__ == '__main__':
    # For development only - use main.py for production
    print("⚠️  For production use, run: python main.py")
    print("🔧 Development server starting...")
    
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
