#!/bin/bash
# Library Management System - Enhanced Docker Deployment Script
# This script supports initial deployment and upgrades with database migrations

set -e

# Parse command line arguments
COMMAND=${1:-initial}  # Default to 'initial' if no argument provided

echo "🚀 Library Management System - Docker Deployment"
echo "================================================"
echo "📋 Mode: $COMMAND"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Function to check application health
check_health() {
    echo "🔍 Checking application health..."
    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker compose exec -T library-app curl -f http://localhost:5000/health >/dev/null 2>&1; then
            echo "✅ Application is healthy!"
            return 0
        fi
        
        echo "⏳ Attempt $attempt/$max_attempts - waiting for application..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "❌ Application failed to start properly"
    echo "📋 Checking logs..."
    docker compose logs library-app
    return 1
}

# Function to run database migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    
    # Run the universal migration script that works with both SQLite and PostgreSQL
    if docker compose exec -T library-app python scripts/migrate_add_thumbnail_url_universal.py; then
        echo "✅ Database migrations completed successfully!"
        return 0
    else
        echo "❌ Database migrations failed!"
        echo "📋 Checking migration logs..."
        docker compose logs library-app
        return 1
    fi
}

# Function to initialize database with sample data (only if empty)
initialize_database() {
    echo "📋 Checking if database needs initialization..."
    
    # Check if database already has data
    if docker compose exec -T library-app python -c "
import sys, os
sys.path.insert(0, '.')
from app import app, db
from models import Book
with app.app_context():
    if Book.query.first():
        print('HAS_DATA')
    else:
        print('EMPTY')
" | grep -q "HAS_DATA"; then
        echo "📚 Database already contains data. Skipping initialization."
        echo "   Your existing data is safe and preserved!"
        return 0
    fi
    
    echo "📋 Database is empty. Initializing with sample data..."
    if docker compose exec -T library-app python scripts/init_postgres.py; then
        echo "✅ Database initialized successfully!"
        return 0
    else
        echo "⚠️  Database initialization failed, but application is running"
        echo "   You can initialize manually later with:"
        echo "   docker compose exec library-app python scripts/init_postgres.py"
        return 1
    fi
}

# Function for initial deployment
initial_deployment() {
    echo "🎯 Starting initial deployment..."
    
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

    echo "🏃 Starting services..."
    docker compose up -d

    echo "⏳ Waiting for services to be ready..."
    echo "   - Starting PostgreSQL database..."
    sleep 15
    echo "   - Starting application..."

    # Check health
    if ! check_health; then
        exit 1
    fi

    # Run migrations
    if ! run_migrations; then
        echo "⚠️  Continuing despite migration failure..."
    fi

    # Initialize database
    initialize_database

    echo ""
    echo "🎉 Initial deployment successful!"
}

# Function for upgrade deployment
upgrade_deployment() {
    echo "🎯 Starting upgrade deployment..."
    
    echo "🔄 Stopping existing services..."
    docker compose down

    echo "🔧 Building updated Docker image..."
    docker compose build --no-cache

    echo "🏃 Starting updated services..."
    docker compose up -d

    echo "⏳ Waiting for services to be ready..."
    sleep 15

    # Check health
    if ! check_health; then
        exit 1
    fi

    # Run migrations
    if ! run_migrations; then
        echo "❌ Upgrade failed due to migration errors!"
        exit 1
    fi

    echo ""
    echo "🎉 Upgrade deployment successful!"
}

# Main execution logic
case "$COMMAND" in
    "initial")
        initial_deployment
        ;;
    "upgrade")
        upgrade_deployment
        ;;
    *)
        echo "❌ Invalid command: $COMMAND"
        echo ""
        echo "Usage: $0 [initial|upgrade]"
        echo ""
        echo "Commands:"
        echo "  initial  - Initial deployment (default)"
        echo "  upgrade  - Upgrade existing deployment with migrations"
        echo ""
        echo "Examples:"
        echo "  $0 initial   # Initial deployment"
        echo "  $0 upgrade   # Upgrade with migrations"
        echo "  $0           # Same as 'initial'"
        exit 1
        ;;
esac

echo ""
echo "📋 Next steps:"
echo "1. Your tunnel should now be able to access: http://library-app:5000"
echo "2. Test the application through your tunnel"
echo ""
echo "🔍 Useful commands:"
echo "  View logs:           docker compose logs -f library-app"
echo "  View DB logs:        docker compose logs -f library-db"
echo "  Stop app:            docker compose down"
echo "  Check health:        docker compose exec library-app curl http://localhost:5000/health"
echo "  Check status:        docker compose ps"
echo "  DB shell:            docker compose exec library-db psql -U libraryuser library"
echo "  Run migrations:      docker compose exec library-app python scripts/migrate_add_thumbnail_url_universal.py"
echo "  Future upgrades:     ./scripts/deploy-cloudflare.sh upgrade"
echo ""
