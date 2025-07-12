# 📚 Library Management System

A modern, feature-rich library management system with advanced QR code and ISBN barcode scanning capabilities. Built with Flask, PostgreSQL, and modern web technologies.

## ✨ Features

### � Book Management
- **Comprehensive Book Database**: Store detailed book information (title, author, ISBN, publisher, etc.)
- **ISBN Barcode Scanning**: Automatic book identification and me## ⚡ Development Workflow

### Feature Development
1. **Setup**: Clone repo and set up development environment
2. **Database**: Run `python scripts/init_db.py` for sample data
3. **Testing**: Use `/system-test` page for manual testing
4. **Debugging**: Enable debug mode with `python main.py --debug`

### Production Deployment Workflow
1. **Development**: Complete feature development and testing locally
2. **Commit**: Push changes to GitHub repository
3. **Cloud Access**: SSH to your cloud server
4. **Update Code**: 
   ```bash
   cd /path/to/integrated-library-system
   git pull origin main
   ```
5. **Deploy**: Execute deployment script manually
   ```bash
   # For updates with potential database changes
   ./scripts/deploy-cloudflare-enhanced.sh upgrade
   
   # For simple restarts
   ./scripts/deploy-cloudflare-enhanced.sh
   ```
6. **Verify**: Check health and functionality
   ```bash
   curl http://localhost:5000/health
   docker-compose logs -f library-app
   ```

### Manual Execution Benefits
- **Full Control**: Monitor each step of the deployment process
- **Debugging**: Immediate access to logs and error messages
- **Customization**: Ability to modify deployment steps as needed
- **Security**: Direct server access without automated triggers
- **Flexibility**: Choose when and how to deploy updates

### Deployment Script Options

#### Enhanced Deployment Script
```bash
# Initial setup (first deployment)
./scripts/deploy-cloudflare-enhanced.sh initial

# Regular updates (after git pull)
./scripts/deploy-cloudflare-enhanced.sh upgrade

# Simple restart (no code changes)
./scripts/deploy-cloudflare-enhanced.sh restart
```

#### Quick Database Fixes
```bash
# Fix missing columns or schema issues
./scripts/quick-fix-thumbnail-column.sh
```

#### Environment-Specific Commands
**Linux/macOS:**
```bash
chmod +x scripts/*.sh
./scripts/deploy-cloudflare-enhanced.sh upgrade
```

**Windows (if using Windows Server):**
```powershell
.\scripts\deploy-cloudflare-enhanced.bat upgrade
.\scripts\quick-fix-thumbnail-column.bat
```
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

### Enhanced Deployment Scripts

#### Automated Deployment Script
For complete deployment with health checks and database migrations:
```bash
# Make script executable
chmod +x scripts/deploy-cloudflare-enhanced.sh

# Initial deployment (fresh install)
./scripts/deploy-cloudflare-enhanced.sh initial

# Upgrade deployment (with migrations)
./scripts/deploy-cloudflare-enhanced.sh upgrade

# Standard deployment (restart services)
./scripts/deploy-cloudflare-enhanced.sh
```

#### Manual Cloud Deployment
If you prefer to execute deployment steps manually on your cloud server:

**Linux/macOS:**
```bash
# Make scripts executable
chmod +x scripts/deploy-cloudflare-enhanced.sh
chmod +x scripts/quick-fix-thumbnail-column.sh

# For first-time setup with missing database columns
./scripts/quick-fix-thumbnail-column.sh

# For regular deployments after git updates
./scripts/deploy-cloudflare-enhanced.sh upgrade
```

**Windows:**
```powershell
# Execute deployment scripts directly
.\scripts\deploy-cloudflare-enhanced.bat upgrade
.\scripts\quick-fix-thumbnail-column.bat
```

#### Deployment Script Features
- **Health Monitoring**: Pre and post-deployment health checks
- **Database Migrations**: Automatic schema updates for new features
- **Service Management**: Intelligent container restart and cleanup
- **Error Handling**: Comprehensive error detection and recovery
- **Rollback Support**: Safe deployment with rollback capabilities

### Cloud Deployment Workflow

#### Initial Setup (First Deployment)
1. **Clone Repository**: `git clone <your-repo>` on cloud server
2. **Environment Setup**: Configure `.env.production` with secure credentials
3. **Database Schema**: Run initial deployment with database setup
4. **Health Verification**: Confirm all services are running correctly

#### Regular Updates (GitHub Pull)
1. **Pull Changes**: `git pull origin main` to get latest code
2. **Run Upgrade**: Execute `./scripts/deploy-cloudflare-enhanced.sh upgrade`
3. **Database Migration**: Script automatically handles schema changes
4. **Service Restart**: Clean restart of all Docker services
5. **Health Check**: Verify deployment success

#### Emergency Fixes
For critical database schema issues (like missing columns):
```bash
# Quick fix for production database issues
./scripts/quick-fix-thumbnail-column.sh
```

### Standard Deployment
```bash
# Use the basic deployment script
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

### Production Deployment Scripts

#### Enhanced Deployment Script (`scripts/deploy-cloudflare-enhanced.sh`)
```bash
# Initial deployment (fresh install)
./scripts/deploy-cloudflare-enhanced.sh initial

# Upgrade deployment (after git pull)
./scripts/deploy-cloudflare-enhanced.sh upgrade

# Standard restart
./scripts/deploy-cloudflare-enhanced.sh
```

**Script Features:**
- Automatic database migration detection
- Health checks before and after deployment
- Container cleanup and optimization
- Error logging and recovery
- Production-ready with PostgreSQL support

#### Quick Fix Script (`scripts/quick-fix-thumbnail-column.sh`)
```bash
# Fix missing database columns in production
./scripts/quick-fix-thumbnail-column.sh
```

**Use Cases:**
- Resolve production database schema mismatches
- Add missing columns after feature updates
- Emergency fixes for database-related deployment failures

#### Manual Cloud Execution Workflow
1. **SSH to Cloud Server**: Connect to your cloud instance
2. **Navigate to Project**: `cd /path/to/integrated-library-system`
3. **Pull Latest Code**: `git pull origin main`
4. **Run Deployment**: `./scripts/deploy-cloudflare-enhanced.sh upgrade`
5. **Verify Health**: Check application is running correctly

### Database Management Scripts

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

### Database Management Scripts
```bash
# Initialize with sample data
docker-compose exec library-app python scripts/init_postgres.py

# Database migrations (if needed)
docker-compose exec library-app python scripts/migrate_books_categories.py

# Universal thumbnail column migration
docker-compose exec library-app python scripts/migrate_add_thumbnail_url_universal.py

# Migrate existing data
docker-compose exec library-app python scripts/migrate_books_genre_to_categories.py
docker-compose exec library-app python scripts/migrate_employee_code.py
docker-compose exec library-app python scripts/migrate_members.py
```

### Production Monitoring Commands
```bash
# Real-time application logs
docker-compose logs -f library-app

# Database logs
docker-compose logs -f library-db

# Check application health
curl http://localhost:5000/health

# Database connection test
docker-compose exec library-app python -c "from app import app, db; app.app_context().push(); print('DB Status:', db.engine.execute('SELECT 1').scalar())"

# Container status
docker-compose ps

# Resource usage
docker stats
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
│   ├── models.py               # Database models (with thumbnail support)
│   ├── config.py               # Configuration classes
│   ├── utils.py                # QR/ISBN utilities
│   └── main.py                 # Application entry point
├── 🎨 Frontend
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── books.html          # Book management with thumbnails
│   │   ├── scanner.html        # QR/barcode scanning interface
│   │   └── ...                 # Other templates
│   └── static/                 # CSS, JavaScript, images
├── 📚 Scripts & Tools
│   ├── scripts/                # Management & deployment scripts
│   │   ├── deploy-cloudflare-enhanced.sh    # Enhanced deployment script
│   │   ├── deploy-cloudflare-enhanced.bat   # Windows deployment script
│   │   ├── quick-fix-thumbnail-column.sh    # Database fix script
│   │   ├── quick-fix-thumbnail-column.bat   # Windows fix script
│   │   ├── migrate_add_thumbnail_url_universal.py  # Universal migration
│   │   └── ...                 # Other utility scripts
│   ├── tests/                  # Test suite
│   └── docs/                   # Documentation
├── 📦 Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env.production.example # Environment template
│   └── README.md              # This file (updated with deployment info)
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

## 🔧 Deployment Troubleshooting

### Common Production Issues

#### Missing Database Columns
**Symptom**: `column "books.thumbnail_url" does not exist`
**Solution**: 
```bash
# Run the quick fix script
./scripts/quick-fix-thumbnail-column.sh

# Or manually add the column
docker-compose exec library-db psql -U libraryuser library -c "ALTER TABLE books ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR(500);"
```

#### Container Startup Issues
**Symptom**: Services fail to start or health checks fail
**Solution**:
```bash
# Check logs for errors
docker-compose logs -f library-app
docker-compose logs -f library-db

# Restart specific service
docker-compose restart library-app

# Full restart
docker-compose down && docker-compose up -d
```

#### Database Connection Issues
**Symptom**: Application cannot connect to PostgreSQL
**Solution**:
```bash
# Check database container status
docker-compose ps library-db

# Test database connectivity
docker-compose exec library-db pg_isready -U libraryuser

# Reset database service
docker-compose restart library-db
```

### Deployment Best Practices

#### Pre-Deployment Checklist
- [ ] Backup production database
- [ ] Test deployment script in staging environment
- [ ] Verify environment variables are set correctly
- [ ] Check disk space and system resources
- [ ] Review application logs for existing issues

#### Post-Deployment Verification
- [ ] Health check: `curl http://localhost:5000/health`
- [ ] Database connectivity: Test book search and member lookup
- [ ] Scanner functionality: Test QR code and barcode scanning
- [ ] File uploads: Verify member card generation works
- [ ] Monitor logs for errors: `docker-compose logs -f library-app`

#### Maintenance Commands
```bash
# Weekly database backup
docker-compose exec library-db pg_dump -U libraryuser library > "backup_$(date +%Y%m%d).sql"

# Clean up unused Docker resources
docker system prune -f

# Update to latest images
docker-compose pull && docker-compose up -d

# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

#### Rollback Procedure
If deployment fails and you need to rollback:
```bash
# Stop current deployment
docker-compose down

# Checkout previous working version
git checkout <previous-commit-hash>

# Deploy previous version
./scripts/deploy-cloudflare-enhanced.sh

# Restore database backup if needed
docker-compose exec -T library-db psql -U libraryuser library < backup_previous.sql
```

---

**Ready to revolutionize your library management? Deploy in minutes with Docker! 🚀**
