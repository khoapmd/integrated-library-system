# Scripts Directory

This directory contains deployment scripts, database migration tools, and utility scripts for the Library Management System.

## 📁 Directory Structure

### 🚀 Deployment Scripts
- **`deploy.sh`** / **`deploy.bat`** - Simple deployment script for basic setup and development
- **`deploy-cloudflare-enhanced.sh`** / **`deploy-cloudflare-enhanced.bat`** - Production deployment with Cloudflare tunnel support, upgrade capabilities, and database migrations

**🛡️ Safety Features:**
- **Database Protection**: Automatically detects existing data and preserves it
- **No Overwriting**: Production databases are never reinitialized or overwritten
- **Additive Migrations**: Only adds new columns/tables, never removes existing data

### 🗄️ Database Scripts
- **`init_db.py`** - Initialize SQLite database with sample data
- **`init_postgres.py`** - Initialize PostgreSQL database for production
- **`migrate_add_search_normalized.py`** - Add normalized search columns for Vietnamese text search
- **`migrate_add_thumbnail_url_universal.py`** - Add thumbnail_url column (works with SQLite & PostgreSQL)
- **`migrate_employee_code.py`** - Add employee_code column to members table
- **`quick-fix-thumbnail-column.sh`** / **`quick-fix-thumbnail-column.bat`** - Quick fix for thumbnail column issues

### 🛠️ Utility Scripts
- **`generate_member_qr.py`** - Generate QR codes for library members
- **`generate_ssl_certs.py`** - Generate self-signed SSL certificates for development
- **`test_migration_safety.py`** - Test database migration safety before production deployment
- **`production_migration_summary.py`** - Display summary of what production migrations will do

## 🔧 Usage

### Quick Start
```bash
# Development/Basic deployment
./scripts/deploy.sh

# Production deployment with Cloudflare tunnel (safe for existing databases)
./scripts/deploy-cloudflare-enhanced.sh initial

# Production upgrades with database migrations (preserves all existing data)
./scripts/deploy-cloudflare-enhanced.sh upgrade
```

**🔒 Production Safety Note**: All deployment scripts include safety checks to prevent data loss. Existing production databases are automatically detected and preserved.

### Database Migrations
```bash
# Run specific migration
python scripts/migrate_add_search_normalized.py

# Test migration safety
python scripts/test_migration_safety.py
```

### Utilities
```bash
# Generate QR codes for members
python scripts/generate_member_qr.py

# Generate SSL certificates
python scripts/generate_ssl_certs.py
```

## 📋 Recent Cleanup (July 25, 2025)

**Removed duplicate/obsolete files:**
- `migrate_add_thumbnail_url.py` (duplicate of universal version)
- `migrate_add_thumbnail_url_simple.py` (duplicate of universal version)
- `migrate_books_categories.py` (obsolete - schema already uses categories)
- `migrate_books_genre_to_categories.py` (obsolete - schema already uses categories)
- `migrate_members.py` (functionality covered by migrate_employee_code.py)
- `deploy-cloudflare.sh` / `deploy-cloudflare.bat` (superseded by enhanced versions)

**Kept essential scripts only** - All remaining scripts are actively used or referenced in documentation.
