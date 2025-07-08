# Library Management System - Complete Setup Guide

## System Overview

This is a complete library management system with the following features:

### 1. Book Management (ISBN Scanning)
- **Purpose**: Add new books to the library database
- **Process**: 
  1. Scan ISBN barcode or enter manually
  2. System fetches book information from Google Books API
  3. Librarian reviews and confirms details
  4. Set number of copies
  5. Book is added to database with unique UUID

### 2. Circulation Management (QR Code Scanning)
- **Purpose**: Handle book check-in and check-out
- **Process**:
  1. Each book has a QR code containing its UUID
  2. Scan QR code to identify book
  3. Select member for transaction
  4. Choose check-out or check-in
  5. System updates book availability and records transaction

## Pages and Functionality

### 1. Home Page (`/`)
- System overview and navigation

### 2. Books Management (`/books`)
- **Add New Books**: ISBN scanning → Google Books API → Form pre-fill
- **View All Books**: List with search and pagination
- **Edit/Delete Books**: Full CRUD operations
- **Generate QR Codes**: For circulation

### 3. Circulation (`/circulation`)
- **QR Code Scanning**: For check-in/check-out
- **Member Selection**: Choose from active members
- **Transaction Recording**: Automatic logging
- **Availability Updates**: Real-time copy tracking

### 4. Members Management (`/members`)
- **Add Members**: Registration form
- **View Members**: List with status
- **Member History**: Transaction records

## Technical Implementation

### Frontend
- **Scanner Module**: Universal scanner for both ISBN and QR codes
- **BarcodeDetector API**: Native browser barcode scanning
- **Camera Access**: Live video scanning
- **File Upload**: Image scanning fallback

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Google Books API**: Book metadata lookup
- **QR Code Generation**: For book identification
- **Transaction Management**: Check-in/out logic

### Database Schema
- **Books**: ISBN, title, author, copies, UUID
- **Members**: Personal info, membership details
- **Transactions**: Borrowing history, due dates, fines

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 3. Add Sample Data (Optional)
```bash
python init_db.py
```

### 4. Run Application
```bash
python app.py
```

### 5. Access System
- Main application: http://localhost:5000
- System test: http://localhost:5000/system_test

## Usage Workflow

### Adding New Books
1. Go to Books page
2. Click "Scan ISBN" or "Add Manually"
3. Scan barcode or enter ISBN
4. Review fetched information
5. Set number of copies
6. Save to database

### Book Circulation
1. Go to Circulation page
2. Scan book QR code
3. Select member
4. Choose check-out or check-in
5. Confirm transaction

### Managing Members
1. Go to Members page
2. Add new members as needed
3. View member transaction history
4. Manage membership status

## API Endpoints

### Book Management
- `GET /api/books` - List all books
- `POST /api/books` - Add new book
- `GET /api/books/isbn/{isbn}` - Find book by ISBN
- `GET /api/books/uuid/{uuid}` - Find book by UUID
- `GET /api/isbn/lookup/{isbn}` - External ISBN lookup

### Circulation
- `POST /api/circulation/checkout` - Check out book
- `POST /api/circulation/checkin` - Check in book
- `GET /api/circulation/history` - Transaction history

### Members
- `GET /api/members` - List members
- `POST /api/members` - Add member

## Testing

### ISBN Scanning Test
- Use ISBN: 9783161484100
- Should fetch book info from Google Books
- Form should pre-fill with book details

### QR Code Test
- Generate QR code for existing book
- Scan with circulation scanner
- Should identify book and show details

### Browser Compatibility
- Chrome/Edge: Full BarcodeDetector support
- Firefox/Safari: Limited support, file upload fallback
- Mobile: Camera access for scanning

## Troubleshooting

### SSL Certificate Errors
- Development mode disables SSL verification
- For production, use proper certificates

### Camera Access Issues
- Ensure HTTPS or localhost
- Grant camera permissions
- Use file upload as fallback

### API Timeout
- External APIs may be slow
- Fallback data provided on errors
- Manual entry always available

## Security Notes

### Development vs Production
- SSL verification disabled in development
- Enable proper SSL for production
- Use environment variables for sensitive data

### Data Privacy
- Member information should be protected
- Consider GDPR compliance
- Implement proper access controls

## Future Enhancements

### Planned Features
- Email notifications for due dates
- Fine calculation and payment
- Advanced reporting and analytics
- Mobile app integration
- Bulk operations
- Export/import functionality

### Technical Improvements
- API rate limiting
- Caching for performance
- Better error handling
- Unit tests
- Documentation generation
