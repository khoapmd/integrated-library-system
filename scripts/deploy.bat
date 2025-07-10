@echo off
REM Simple deployment script for library management system

echo 🚀 Starting Library Management System
echo ====================================

REM Check if .env.production exists
if not exist ".env.production" (
    echo 📝 Creating .env.production from example...
    copy .env.production.example .env.production
    echo ⚠️  Please edit .env.production and set your passwords!
    pause
)

echo 🔧 Building and starting services...
docker-compose up -d --build

echo ⏳ Waiting for services...
timeout /t 10 /nobreak >nul

echo 🔍 Checking status...
docker-compose ps

echo ✅ Done! Check your tunnel to access the app.
pause
