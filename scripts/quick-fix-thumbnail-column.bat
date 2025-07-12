@echo off
REM Quick fix for production database - Add thumbnail_url column
REM Run this to fix the immediate issue

echo 🔧 Quick Fix: Adding thumbnail_url column to production database
echo =============================================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

REM Check if the container is running
docker compose ps library-app | findstr "running" >nul
if errorlevel 1 (
    echo ❌ Library app container is not running. Please start it first with:
    echo    docker compose up -d
    exit /b 1
)

echo 🔄 Adding thumbnail_url column to PostgreSQL database...

REM Run the SQL command directly
docker compose exec -T library-db psql -U libraryuser library -c "DO $$ BEGIN IF NOT EXISTS (SELECT column_name FROM information_schema.columns WHERE table_name = 'books' AND column_name = 'thumbnail_url') THEN ALTER TABLE books ADD COLUMN thumbnail_url VARCHAR(500); RAISE NOTICE 'Added thumbnail_url column to books table'; ELSE RAISE NOTICE 'thumbnail_url column already exists'; END IF; END $$;"

if not errorlevel 1 (
    echo ✅ Successfully added thumbnail_url column!
    echo.
    echo 🔄 Restarting application to apply changes...
    docker compose restart library-app
    
    echo ⏳ Waiting for application to restart...
    timeout /t 10 >nul
    
    REM Test if the app is working
    docker compose exec -T library-app curl -f http://localhost:5000/health >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Application is running successfully!
        echo.
        echo 🎉 Quick fix completed! Your application should now work properly.
        echo.
        echo 📋 Next time you update from GitHub, use:
        echo    .\scripts\deploy-cloudflare-enhanced.bat upgrade
    ) else (
        echo ⚠️  Application may need more time to start. Check with:
        echo    docker compose logs library-app
    )
) else (
    echo ❌ Failed to add column. Please check the database connection.
    echo 📋 Debugging commands:
    echo    docker compose logs library-db
    echo    docker compose exec library-db psql -U libraryuser library
)
