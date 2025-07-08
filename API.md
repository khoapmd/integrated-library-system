# API Documentation

## Base URL
`http://localhost:5000/api`

## Authentication
Currently, no authentication is required. In production, you should implement proper authentication and authorization.

## Book Management

### Get All Books
- **GET** `/books`
- **Parameters:**
  - `page` (optional): Page number (default: 1)
  - `per_page` (optional): Items per page (default: 10)
  - `search` (optional): Search query for title, author, or ISBN
- **Response:**
```json
{
  "books": [...],
  "total": 50,
  "pages": 5,
  "current_page": 1
}
```

### Add New Book
- **POST** `/books`
- **Body:**
```json
{
  "isbn": "9780134685991",
  "title": "Effective Java",
  "author": "Joshua Bloch",
  "publisher": "Addison-Wesley Professional",
  "genre": "Programming",
  "description": "A comprehensive guide...",
  "language": "English",
  "pages": 416,
  "location": "A1-001",
  "copies_total": 3,
  "copies_available": 3
}
```

### Get Book by ID
- **GET** `/books/{id}`
- **Response:** Book object

### Update Book
- **PUT** `/books/{id}`
- **Body:** Partial book object with fields to update

### Delete Book
- **DELETE** `/books/{id}`

### Get Book by UUID
- **GET** `/books/uuid/{uuid}`
- **Response:** Book object (used for QR code scanning)

## QR Code Management

### Generate QR Code
- **GET** `/qr/{book_id}`
- **Response:**
```json
{
  "success": true,
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "book": {...}
}
```

### Scan QR Code
- **POST** `/scan/qr`
- **Body:** Form data with `image` file
- **Response:**
```json
{
  "success": true,
  "books": [...],
  "raw_results": [...]
}
```

## ISBN Scanning

### Scan ISBN from Image
- **POST** `/scan/isbn`
- **Body:** Form data with `image` file
- **Response:**
```json
{
  "success": true,
  "books": [...],
  "isbn_results": [...]
}
```

### Get Book Info by ISBN
- **GET** `/isbn/{isbn}`
- **Response:**
```json
{
  "success": true,
  "book_info": {
    "isbn": "9780134685991",
    "title": "Effective Java",
    "authors": ["Joshua Bloch"],
    "author": "Joshua Bloch",
    "publisher": "Addison-Wesley Professional",
    "publication_date": "2017",
    "language": "English",
    "description": "",
    "cover_url": "https://...",
    "pages": null
  }
}
```

## Member Management

### Get All Members
- **GET** `/members`
- **Response:** Array of member objects

### Add New Member
- **POST** `/members`
- **Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "phone": "+1-555-0123",
  "address": "123 Main St, City, State 12345",
  "membership_type": "regular",
  "max_books": 5
}
```

## Transaction Management

### Get All Transactions
- **GET** `/transactions`
- **Response:** Array of transaction objects

### Borrow Book
- **POST** `/borrow`
- **Body:**
```json
{
  "book_id": 1,
  "member_id": 1
}
```

### Return Book
- **POST** `/return`
- **Body:**
```json
{
  "transaction_id": 1
}
```

## Error Responses

All endpoints may return error responses in the following format:
```json
{
  "success": false,
  "message": "Error description"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Data Models

### Book
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "isbn": "9780134685991",
  "title": "Effective Java",
  "author": "Joshua Bloch",
  "publisher": "Addison-Wesley Professional",
  "publication_date": "2017-12-27",
  "genre": "Programming",
  "description": "A comprehensive guide...",
  "language": "English",
  "pages": 416,
  "location": "A1-001",
  "status": "available",
  "copies_total": 3,
  "copies_available": 3,
  "added_date": "2025-01-01T00:00:00",
  "last_updated": "2025-01-01T00:00:00"
}
```

### Member
```json
{
  "id": 1,
  "member_id": "LIB001",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "phone": "+1-555-0123",
  "address": "123 Main St, City, State 12345",
  "membership_date": "2025-01-01T00:00:00",
  "membership_type": "regular",
  "status": "active",
  "max_books": 5
}
```

### Transaction
```json
{
  "id": 1,
  "book_id": 1,
  "member_id": 1,
  "transaction_type": "borrow",
  "transaction_date": "2025-01-01T00:00:00",
  "due_date": "2025-01-15T00:00:00",
  "return_date": null,
  "fine_amount": 0.0,
  "status": "active",
  "notes": null
}
```
