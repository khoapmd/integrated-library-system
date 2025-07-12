# 📚 Library Management System

A modern, feature-rich library management system with advanced QR code and ISBN barcode scanning capabilities. Built with Flask, PostgreSQL, and modern web technologies.

## ✨ Features

### � Book Management
- **Comprehensive Book Database**: Store detailed book information (title, author, ISBN, publisher, etc.)
- **ISBN Barcode Scanning**: Automatic book identification and metadata lookup
- **Multi-Service ISBN Lookup**: Fetches book data from Google Books and other sources
- **QR Code Generation**: Automatic QR code generation for each book
- **Inventory Tracking**: Track total copies and availability

### 👥 Member Management  
- **Member Registration**: Complete member profiles with contact information
- **Employee Integration**: Support for employee codes and departments
- **Member QR Codes**: Generate QR codes for quick member identification
- **Borrowing Limits**: Configurable maximum books per member

### 🔄 Circulation System
- **Dual Scanning Support**: QR codes and ISBN barcodes
- **Smart Check-out/Check-in**: Automatic due date calculation
- **Book Condition Tracking**: Record book condition on return
- **Fine Management**: Automatic overdue fine calculation
- **Manual Entry Option**: Keyboard input for identifiers when scanning isn't available

### 🖥️ Modern Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Scanner**: Browser-based camera scanning
- **Dashboard**: Overview of library statistics and recent activity
- **Advanced Search**: Multi-field search capabilities
- **Toast Notifications**: User-friendly feedback system

### 🔧 Technical Features
- **PostgreSQL Database**: Robust production database
- **Health Monitoring**: Built-in health checks for deployment
- **Docker Support**: Container-ready for easy deployment
- **Cloudflare Tunnel Ready**: Optimized for reverse proxy deployment
- **Security**: ProxyFix middleware, secure sessions, input validation

## 🐳 Production Deployment (Docker + PostgreSQL)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd library-management-system

# Configure environment
cp .env.production.example .env.production
# Edit .env.production with your secure passwords

# Deploy with Docker Compose
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Full Deployment with Health Checks
```bash
# Use the comprehensive deployment script
chmod +x scripts/deploy-cloudflare.sh
./scripts/deploy-cloudflare.sh
```

### Docker Compose Services
- **library-app**: Flask application server
- **library-db**: PostgreSQL 15 database
- **Volumes**: Persistent storage for database, uploads, logs
- **Networks**: Ready for Cloudflare tunnel integration

### Environment Configuration
```env
# Required: Set secure passwords
SECRET_KEY=your-super-secret-production-key-here
POSTGRES_PASSWORD=your-secure-database-password-here

# Optional: Customize database
POSTGRES_DB=library
POSTGRES_USER=libraryuser

# Security (for reverse proxy deployment)
SESSION_COOKIE_SECURE=true
PREFERRED_URL_SCHEME=https
```

## 🌐 Cloudflare Tunnel Integration

Perfect for secure remote access without exposing ports:

1. **Network Setup**: App connects to `access_tunnel` network
2. **Service Configuration**: Point tunnel to `http://library-app:5000`
3. **Security**: Built-in ProxyFix middleware handles proxy headers
4. **SSL Termination**: Cloudflare handles SSL, app runs HTTP internally

See `docs/CLOUDFLARE_DEPLOYMENT.md` for detailed setup instructions.

## 💻 Local Development

### Prerequisites
- Python 3.12
- pip package manager

### Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize development database
python scripts/init_db.py

# Run development server
python main.py --debug
```

### Development Features
- **Hot Reload**: Automatic restart on code changes
- **SQLite Database**: Lightweight development database
- **Debug Mode**: Detailed error messages and debugging
- **HTTPS Support**: Generate SSL certificates with `scripts/generate_ssl_certs.py`

## 🔍 Scanner Capabilities

### Supported Formats
- **Book QR Codes**: Library-generated book QR codes with UUID
- **ISBN Barcodes**: EAN-13, UPC-A, and other ISBN barcode formats
- **Manual Entry**: UUID, ISBN-10, ISBN-13, or barcode numbers

### Browser Compatibility
- **Modern Browsers**: Uses native BarcodeDetector API
- **Fallback Support**: ZXing library for older browsers
- **Camera Access**: Automatic camera permission handling
- **Multiple Cameras**: Support for front/back camera selection

### Scanning Features
- **Real-time Scanning**: Live camera preview with instant recognition
- **Multiple Code Types**: Simultaneous QR and barcode detection
- **Auto-stop**: Automatically stops scanning after successful detection
- **Error Handling**: Graceful fallbacks and user feedback

## 📋 Management Commands

### Docker Commands
```bash
# View logs
docker-compose logs -f library-app

# Check health
docker-compose exec library-app curl http://localhost:5000/health

# Database shell
docker-compose exec library-db psql -U libraryuser library

# Backup database
docker-compose exec library-db pg_dump -U libraryuser library > backup.sql

# Stop services
docker-compose down
```

### Database Management
```bash
# Initialize with sample data
docker-compose exec library-app python scripts/init_postgres.py

# Database migrations (if needed)
docker-compose exec library-app python scripts/migrate_books_categories.py
```

## 🛡️ Security Features

### Production Security
- **Secure Sessions**: HTTPOnly, Secure, SameSite cookies
- **Proxy Trust**: ProxyFix middleware for reverse proxy deployment
- **Input Validation**: Comprehensive form and API validation
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **File Upload Security**: Safe file handling with size limits

### Environment Security
- **Secret Management**: Environment variable configuration
- **Database Credentials**: Secure password handling
- **SSL/TLS**: HTTPS support with certificate management
- **Rate Limiting**: Built-in protection against abuse

## � API Endpoints

### Books
- `GET /api/books` - List books with pagination and search
- `POST /api/books` - Add new book or update existing
- `GET /api/books/isbn/<isbn>` - Get book by ISBN
- `GET /api/books/uuid/<uuid>` - Get book by UUID
- `POST /api/isbn/lookup/<isbn>` - External ISBN metadata lookup

### Members
- `GET /api/members` - List all members
- `POST /api/members` - Add new member
- `GET /api/members/employee/<code>` - Get member by employee code
- `PUT /api/members/<id>` - Update member
- `DELETE /api/members/<id>` - Delete member

### Circulation
- `POST /api/circulation/checkout` - Check out book
- `POST /api/circulation/checkin` - Check in book with condition
- `GET /api/circulation/status/<uuid>` - Get book circulation status
- `GET /api/circulation/recent` - Recent transactions

### Health & Monitoring
- `GET /health` - Application health check
- `GET /ready` - Readiness check for orchestration

## 🧪 Testing

### Test Suite
```bash
# Run all tests
python -m pytest tests/

# Run specific components
python -m pytest tests/test_circulation_scanner.py
python -m pytest tests/test_member_lookup.py

# Coverage report
python -m pytest tests/ --cov=.
```

### Manual Testing
- **System Test Page**: `/system-test` - Comprehensive feature testing
- **Scanner Debug**: `/debug-scanner` - Scanner functionality testing
- **QR Generator**: `/qr-generator` - Generate test QR codes

## 📁 Project Structure

```
library-management-system/
├── 🐳 Docker Configuration
│   ├── Dockerfile              # Production container
│   ├── docker-compose.yml      # Services orchestration
│   └── .dockerignore           # Docker build optimization
├── ⚙️ Application Core
│   ├── app.py                  # Flask application & routes
│   ├── models.py               # Database models
│   ├── config.py               # Configuration classes
│   ├── utils.py                # QR/ISBN utilities
│   └── main.py                 # Application entry point
├── 🎨 Frontend
│   ├── templates/              # Jinja2 HTML templates
│   └── static/                 # CSS, JavaScript, images
├── 📚 Scripts & Tools
│   ├── scripts/                # Management scripts
│   ├── tests/                  # Test suite
│   └── docs/                   # Documentation
├── 📦 Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env.production.example # Environment template
│   └── README.md              # This file
└── 💾 Data (Runtime)
    ├── instance/               # SQLite database (dev)
    ├── uploads/                # File uploads
    ├── member_cards/           # Generated QR codes
    └── logs/                   # Application logs
```

## � Development Workflow

### Feature Development
1. **Setup**: Clone repo and set up development environment
2. **Database**: Run `python scripts/init_db.py` for sample data
3. **Testing**: Use `/system-test` page for manual testing
4. **Debugging**: Enable debug mode with `python main.py --debug`

### Production Deployment
1. **Environment**: Configure `.env.production` with secure values
2. **Build**: Run deployment script `./scripts/deploy-cloudflare.sh`
3. **Monitor**: Check health endpoints and Docker logs
4. **Backup**: Regular database backups with provided commands

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python -m pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Documentation

### Documentation
- **API Documentation**: `docs/API.md`
- **Docker Deployment**: `docs/DOCKER_DEPLOYMENT.md`
- **Cloudflare Setup**: `docs/CLOUDFLARE_DEPLOYMENT.md`
- **Scanner Guide**: `docs/ENHANCED_SCANNING_README.md`

### Troubleshooting
- Check Docker logs: `docker-compose logs -f`
- Health check: `curl http://localhost:5000/health`
- Database status: `docker-compose ps`

### Getting Help
1. Check the documentation in `docs/` folder
2. Review existing issues in the repository
3. Create a new issue with detailed description

## 🙏 Acknowledgments

- **Flask**: Web framework and ecosystem
- **PostgreSQL**: Robust database system
- **SQLAlchemy**: Object-relational mapping
- **ZXing**: Barcode scanning library
- **OpenCV & pyzbar**: Computer vision libraries
- **Bootstrap**: Responsive UI framework
- **Font Awesome**: Icon library

---

**Ready to revolutionize your library management? Deploy in minutes with Docker! 🚀**
