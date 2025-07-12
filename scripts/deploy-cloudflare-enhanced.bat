@echo off
REM Library Management System - Enhanced Docker Deployment Script for Windows
REM This script supports initial deployment and upgrades with database migrations

setlocal EnableDelayedExpansion

REM Parse command line arguments
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=initial

echo 🚀 Library Management System - Docker Deployment
echo ================================================
echo 📋 Mode: %COMMAND%
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

REM Function to check application health
:check_health
echo 🔍 Checking application health...
set max_attempts=30
set attempt=1

:health_loop
docker compose exec -T library-app curl -f http://localhost:5000/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Application is healthy!
    goto :eof
)

echo ⏳ Attempt !attempt!/!max_attempts! - waiting for application...
timeout /t 2 >nul
set /a attempt+=1
if !attempt! leq !max_attempts! goto health_loop

echo ❌ Application failed to start properly
echo 📋 Checking logs...
docker compose logs library-app
exit /b 1

REM Function to run database migrations
:run_migrations
echo 🔄 Running database migrations...
docker compose exec -T library-app python scripts/migrate_add_thumbnail_url_universal.py
if not errorlevel 1 (
    echo ✅ Database migrations completed successfully!
    goto :eof
) else (
    echo ❌ Database migrations failed!
    echo 📋 Checking migration logs...
    docker compose logs library-app
    exit /b 1
)

REM Function to initialize database
:initialize_database
echo 📋 Initializing database with sample data...
docker compose exec -T library-app python scripts/init_postgres.py
if not errorlevel 1 (
    echo ✅ Database initialized successfully!
) else (
    echo ⚠️  Database initialization failed, but application is running
    echo    You can initialize manually later with:
    echo    docker compose exec library-app python scripts/init_postgres.py
)
goto :eof

REM Main execution logic
if "%COMMAND%"=="initial" goto initial_deployment
if "%COMMAND%"=="upgrade" goto upgrade_deployment

echo ❌ Invalid command: %COMMAND%
echo.
echo Usage: %0 [initial^|upgrade]
echo.
echo Commands:
echo   initial  - Initial deployment (default)
echo   upgrade  - Upgrade existing deployment with migrations
echo.
echo Examples:
echo   %0 initial   # Initial deployment
echo   %0 upgrade   # Upgrade with migrations
echo   %0           # Same as 'initial'
exit /b 1

:initial_deployment
echo 🎯 Starting initial deployment...

REM Check if .env.production exists
if not exist ".env.production" (
    echo 📝 Creating production environment file...
    copy ".env.production.example" ".env.production"
    echo ⚠️  Please edit .env.production with your production values before continuing!
    echo    Set secure SECRET_KEY and POSTGRES_PASSWORD
    echo    Then run this script again.
    exit /b 1
)

REM Check for placeholder values
findstr /C:"your-super-secret-production-key-here" .env.production >nul
if not errorlevel 1 (
    echo ❌ Please set a secure SECRET_KEY in .env.production
    exit /b 1
)

findstr /C:"change-this-password" .env.production >nul
if not errorlevel 1 (
    echo ❌ Please set a secure POSTGRES_PASSWORD in .env.production
    exit /b 1
)

echo 🔧 Building Docker image...
docker compose build --no-cache

echo 🏃 Starting services...
docker compose up -d

echo ⏳ Waiting for services to be ready...
echo    - Starting PostgreSQL database...
timeout /t 15 >nul
echo    - Starting application...

REM Check health
call :check_health
if errorlevel 1 exit /b 1

REM Run migrations
call :run_migrations
if errorlevel 1 (
    echo ⚠️  Continuing despite migration failure...
)

REM Initialize database
call :initialize_database

echo.
echo 🎉 Initial deployment successful!
goto show_commands

:upgrade_deployment
echo 🎯 Starting upgrade deployment...

echo 🔄 Stopping existing services...
docker compose down

echo 🔧 Building updated Docker image...
docker compose build --no-cache

echo 🏃 Starting updated services...
docker compose up -d

echo ⏳ Waiting for services to be ready...
timeout /t 15 >nul

REM Check health
call :check_health
if errorlevel 1 exit /b 1

REM Run migrations
call :run_migrations
if errorlevel 1 (
    echo ❌ Upgrade failed due to migration errors!
    exit /b 1
)

echo.
echo 🎉 Upgrade deployment successful!
goto show_commands

:show_commands
echo.
echo 📋 Next steps:
echo 1. Your tunnel should now be able to access: http://library-app:5000
echo 2. Test the application through your tunnel
echo.
echo 🔍 Useful commands:
echo   View logs:           docker compose logs -f library-app
echo   View DB logs:        docker compose logs -f library-db
echo   Stop app:            docker compose down
echo   Check health:        docker compose exec library-app curl http://localhost:5000/health
echo   Check status:        docker compose ps
echo   DB shell:            docker compose exec library-db psql -U libraryuser library
echo   Run migrations:      docker compose exec library-app python scripts/migrate_add_thumbnail_url_universal.py
echo   Future upgrades:     .\scripts\deploy-cloudflare-enhanced.bat upgrade
echo.
