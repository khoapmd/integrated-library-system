#!/bin/bash
# Simple deployment script for library management system on Ubuntu

echo "🚀 Starting Library Management System"
echo "===================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "📝 Creating .env.production from example..."
    cp .env.production.example .env.production
    echo "⚠️  Please edit .env.production and set your passwords!"
    echo "   Then run this script again."
    exit 1
fi

# Check for placeholder values
if grep -q "change-this-password" .env.production; then
    echo "❌ Please set secure passwords in .env.production"
    exit 1
fi

echo "🔧 Building and starting services..."
docker compose up -d --build

echo "⏳ Waiting for services..."
sleep 10

echo "🔍 Checking status..."
docker compose ps

echo "✅ Done! Your app should be accessible through your tunnel at: library-app:5000"
