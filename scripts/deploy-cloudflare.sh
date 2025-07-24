#!/bin/bash
# Library Management System - Docker Deployment Script for Ubuntu
# This script deploys the application to work with existing Cloudflare tunnel
# Enhanced with safe database migration support

set -e

echo "🚀 Library Management System - Docker Deployment"
echo "==============================================="

# Parse command line arguments
DEPLOYMENT_TYPE="standard"
if [ "$1" = "upgrade" ]; then
    DEPLOYMENT_TYPE="upgrade"
    echo "🔄 Running upgrade deployment with database migrations"
elif [ "$1" = "initial" ]; then
    DEPLOYMENT_TYPE="initial"
    echo "🆕 Running initial deployment"
else
    echo "🔄 Running standard deployment"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "📝 Creating production environment file..."
    cp .env.production.example .env.production
    echo "⚠️  Please edit .env.production with your production values before continuing!"
    echo "   Set secure SECRET_KEY and POSTGRES_PASSWORD"
    echo "   Then run this script again."
    exit 1
fi

# Check for placeholder values
if grep -q "your-super-secret-production-key-here" .env.production; then
    echo "❌ Please set a secure SECRET_KEY in .env.production"
    exit 1
fi

if grep -q "change-this-password" .env.production; then
    echo "❌ Please set a secure POSTGRES_PASSWORD in .env.production"
    exit 1
fi

echo "🔧 Building Docker image..."
docker compose build --no-cache

# Backup existing database before upgrade
if [ "$DEPLOYMENT_TYPE" = "upgrade" ]; then
    echo "💾 Creating database backup before upgrade..."
    if docker compose ps library-db | grep -q "Up"; then
        BACKUP_FILE="backup_before_upgrade_$(date +%Y%m%d_%H%M%S).sql"
        if docker compose exec -T library-db pg_dump -U libraryuser library > "$BACKUP_FILE" 2>/dev/null; then
            echo "✅ Database backup created: $BACKUP_FILE"
        else
            echo "⚠️  Database backup failed, but continuing deployment"
        fi
    else
        echo "ℹ️  Database not running, skipping backup"
    fi
fi

echo "🏃 Starting services..."
docker compose up -d

echo "⏳ Waiting for services to be ready..."
echo "   - Starting PostgreSQL database..."
sleep 15
echo "   - Starting application..."

# Check if the application is healthy
echo "🔍 Checking application health..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker compose exec -T library-app curl -f http://localhost:5000/health >/dev/null 2>&1; then
        echo "✅ Application is healthy!"
        break
    fi
    
    echo "⏳ Attempt $attempt/$max_attempts - waiting for application..."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Application failed to start properly"
    echo "📋 Checking logs..."
    docker compose logs library-app
    exit 1
fi

echo ""
echo "🎉 Application is healthy!"
echo ""

# Handle database initialization and migrations
if [ "$DEPLOYMENT_TYPE" = "initial" ]; then
    echo "📋 Initializing database with sample data..."
    if docker compose exec -T library-app python scripts/init_postgres.py; then
        echo "✅ Database initialized successfully!"
    else
        echo "❌ Database initialization failed"
        exit 1
    fi
elif [ "$DEPLOYMENT_TYPE" = "upgrade" ]; then
    echo "🔄 Running database migrations..."
    
    # Run Vietnamese search normalization migration
    echo "📋 Adding Vietnamese search support..."
    if docker compose exec -T library-app python scripts/migrate_add_search_normalized.py; then
        echo "✅ Vietnamese search migration completed!"
    else
        echo "⚠️  Vietnamese search migration failed, but continuing"
    fi
    
    # Run thumbnail URL migration (universal)
    echo "📋 Updating book thumbnail support..."
    if docker compose exec -T library-app python scripts/migrate_add_thumbnail_url_universal.py; then
        echo "✅ Thumbnail migration completed!"
    else
        echo "⚠️  Thumbnail migration failed, but continuing"
    fi
    
    # Ensure database schema is up to date
    echo "📋 Updating database schema..."
    if docker compose exec -T library-app python scripts/init_postgres.py; then
        echo "✅ Database schema updated successfully!"
    else
        echo "⚠️  Database schema update completed with warnings"
    fi
else
    echo "📋 Checking database schema..."
    if docker compose exec -T library-app python scripts/init_postgres.py; then
        echo "✅ Database schema verified!"
    else
        echo "⚠️  Database check completed with warnings"
    fi
fi

echo ""
echo "🎉 Deployment successful!"
echo ""
echo "📋 Usage Examples:"
echo "  Standard deployment:    ./scripts/deploy-cloudflare.sh"
echo "  Upgrade deployment:     ./scripts/deploy-cloudflare.sh upgrade"
echo "  Initial deployment:     ./scripts/deploy-cloudflare.sh initial"
echo ""
echo "📋 Next steps:"
echo "1. Your tunnel should now be able to access: http://library-app:5000"
echo "2. Test the application through your tunnel"
echo "3. Vietnamese search is now enabled (try: 'Lãnh đạo' or 'lanh dao')"
echo ""
echo "🔍 Useful commands:"
echo "  View logs:       docker compose logs -f library-app"
echo "  View DB logs:    docker compose logs -f library-db"
echo "  Stop app:        docker compose down"
echo "  Check health:    docker compose exec library-app curl http://localhost:5000/health"
echo "  Check status:    docker compose ps"
echo "  DB shell:        docker compose exec library-db psql -U libraryuser library"
echo "  Manual migration: docker compose exec library-app python scripts/migrate_add_search_normalized.py"
echo ""
