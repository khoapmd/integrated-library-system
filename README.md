# Library Management System

A modern, web-based library management system with advanced QR code and ISBN scanning capabilities.

## 🌟 Features

- **📚 Book Management**: Add, edit, and organize your library collection
- **👥 Member Management**: Manage library members and membership details
- **🔄 Circulation System**: Check-in/check-out with QR code scanning
- **📱 QR Code Generation**: Automatic QR code generation for books
- **📖 ISBN Lookup**: Multi-service ISBN lookup with fallback support
- **🔍 Advanced Search**: Search books by title, author, ISBN, or QR code
- **📊 Dashboard**: Real-time statistics and recent activity
- **🔒 Secure**: SSL support and secure data handling

## 🏗️ Project Structure

```
library-management-system/
├── app.py               # Flask application
├── models.py            # Database models
├── config.py            # Configuration settings
├── utils.py             # Utility functions
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates
├── static/             # CSS, JS, and static assets
├── tests/              # Test suite
├── scripts/            # Utility scripts
├── docs/               # Documentation
├── data/               # Sample data
└── instance/           # Database and instance files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd library-management-system
   ```

## 🐳 Docker Deployment (Recommended for Production)

### Quick Start
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t library-management .
docker run -d -p 5000:5000 --name library-app library-management
```

### Access the Application
- Open your browser to `http://localhost:5000`
- For production deployment, see `docs/DOCKER_DEPLOYMENT.md`

## 💻 Local Development

### Prerequisites
- Python 3.8 or higher
- pip package manager

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   # HTTP (development)
   python main.py
   
   # HTTPS (requires SSL certificates)
   python main.py --https
   
   # Custom port
   python main.py --port 8080
   
   # Debug mode
   python main.py --debug
   ```

5. **Access the application**
   - HTTP: http://localhost:5000
   - HTTPS: https://localhost:5000

## 🔧 Configuration

### Environment Variables

- `FLASK_ENV`: Set to `development`, `production`, or `testing`
- `DATABASE_URL`: Custom database URL (optional)
- `SECRET_KEY`: Flask secret key for sessions

### SSL Certificates

For HTTPS support, generate SSL certificates:

```bash
python scripts/generate_ssl_certs.py
```

## 📖 Usage

### Adding Books

1. Navigate to the Books page
2. Click "Add New Book"
3. Enter book details manually or scan ISBN barcode
4. System automatically fetches metadata from multiple sources

### Managing Members

1. Go to Members page
2. Add member details
3. Generate member QR codes for quick identification

### Circulation

1. Use the Circulation page for check-in/check-out
2. Scan book QR codes or member codes
3. System automatically handles due dates and fines

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_app.py

# Run with coverage
python -m pytest tests/ --cov=src
```

## 📚 API Documentation

The system provides RESTful APIs for all operations. See `docs/API.md` for detailed documentation.

### Key Endpoints

- `GET /api/books` - List all books
- `POST /api/books` - Add new book
- `GET /api/members` - List all members
- `POST /api/circulation/checkout` - Check out a book
- `POST /api/circulation/checkin` - Check in a book

## 🛠️ Development

### Running in Development Mode

```bash
# Quick development server
python src/app.py

# Or with the main entry point
python main.py --debug
```

### Database Management

```bash
# Initialize database
python scripts/init_db.py

# Migrate existing data
python scripts/migrate_members.py
```

## 🔒 Security

- SSL/HTTPS support
- Input validation and sanitization
- Secure file upload handling
- Session management
- SQL injection protection via SQLAlchemy ORM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the documentation in the `docs/` folder
2. Review existing issues in the repository
3. Create a new issue for bugs or feature requests

## 🙏 Acknowledgments

- Flask web framework
- SQLAlchemy ORM
- QRCode library for QR code generation
- ISBN library for book metadata lookup
- OpenCV and pyzbar for barcode scanning
