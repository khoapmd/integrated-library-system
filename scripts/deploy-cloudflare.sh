#!/bin/bash
# Library Management System - Docker Deployment Script for Ubuntu
# This script deploys the application to work with existing Cloudflare tunnel

set -e

echo "🚀 Library Management System - Docker Deployment"
echo "==============================================="

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
echo "📋 Initializing database with sample data..."
if docker compose exec -T library-app python scripts/init_postgres.py; then
    echo "✅ Database initialized successfully!"
else
    echo "⚠️  Database initialization failed, but application is running"
    echo "   You can initialize manually later with:"
    echo "   docker compose exec library-app python scripts/init_postgres.py"
fi

echo ""
echo "🎉 Deployment successful!"
echo ""
echo "📋 Next steps:"
echo "1. Your tunnel should now be able to access: http://library-app:5000"
echo "2. Test the application through your tunnel"
echo ""
echo "🔍 Useful commands:"
echo "  View logs:       docker compose logs -f library-app"
echo "  View DB logs:    docker compose logs -f library-db"
echo "  Stop app:        docker compose down"
echo "  Check health:    docker compose exec library-app curl http://localhost:5000/health"
echo "  Check status:    docker compose ps"
echo "  DB shell:        docker compose exec library-db psql -U libraryuser library"
echo ""
