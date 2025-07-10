@echo off
REM Library Management System - Docker Deployment Script
REM This script deploys the application to work with existing Cloudflare tunnel

echo 🚀 Library Management System - Docker Deployment
echo ===============================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

REM Check if .env.production exists
if not exist ".env.production" (
    echo 📝 Creating production environment file...
    copy .env.production.example .env.production
    echo ⚠️  Please edit .env.production with your production values before continuing!
    echo    Set secure SECRET_KEY and POSTGRES_PASSWORD
    pause
)

REM Check for placeholder values
findstr "your-super-secret-production-key-here" .env.production >nul
if not errorlevel 1 (
    echo ❌ Please set a secure SECRET_KEY in .env.production
    exit /b 1
)

findstr "change-this-password" .env.production >nul
if not errorlevel 1 (
    echo ❌ Please set a secure POSTGRES_PASSWORD in .env.production
    exit /b 1
)

echo 🔧 Building Docker image...
docker-compose build --no-cache
if errorlevel 1 (
    echo ❌ Failed to build Docker image
    exit /b 1
)

echo 🏃 Starting services...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    exit /b 1
)

echo ⏳ Waiting for services to be ready...
echo    - Starting PostgreSQL database...
timeout /t 15 /nobreak >nul
echo    - Starting application...

REM Check if the application is healthy
echo 🔍 Checking application health...
set max_attempts=30
set attempt=1

:healthcheck
curl -f http://localhost:5000/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Application is healthy!
    goto :success
)

echo ⏳ Attempt %attempt%/%max_attempts% - waiting for application...
timeout /t 2 /nobreak >nul
set /a attempt+=1
if %attempt% leq %max_attempts% goto :healthcheck

echo ❌ Application failed to start properly
echo 📋 Checking logs...
docker-compose logs library-app
exit /b 1

:success
echo.
echo 🎉 Application is healthy!
echo.
echo 📋 Initializing database with sample data...
docker-compose exec -T library-app python scripts/init_postgres.py
if errorlevel 1 (
    echo ⚠️  Database initialization failed, but application is running
    echo    You can initialize manually later with:
    echo    docker-compose exec library-app python scripts/init_postgres.py
) else (
    echo ✅ Database initialized successfully!
)

echo.
echo 🎉 Deployment successful!
echo.
echo 📋 Next steps:
echo 1. Your tunnel should now be able to access: http://library-app:5000
echo 2. Test the application through your tunnel
echo.
echo 🔍 Useful commands:
echo   View logs:       docker-compose logs -f library-app
echo   View DB logs:    docker-compose logs -f db
echo   Stop app:        docker-compose down
echo   Check health:    docker-compose exec library-app curl http://localhost:5000/health
echo   Check status:    docker-compose ps
echo   DB shell:        docker-compose exec db psql -U libraryuser library
echo.
pause
