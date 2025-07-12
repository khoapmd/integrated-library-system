#!/bin/bash
# Quick fix for production database - Add thumbnail_url column
# Run this to fix the immediate issue

echo "🔧 Quick Fix: Adding thumbnail_url column to production database"
echo "============================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if the container is running
if ! docker compose ps library-app | grep -q "running"; then
    echo "❌ Library app container is not running. Please start it first with:"
    echo "   docker compose up -d"
    exit 1
fi

echo "🔄 Adding thumbnail_url column to PostgreSQL database..."

# Run the SQL command directly
docker compose exec -T library-db psql -U libraryuser library -c "
    DO \$\$ 
    BEGIN 
        IF NOT EXISTS (
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'books' AND column_name = 'thumbnail_url'
        ) THEN
            ALTER TABLE books ADD COLUMN thumbnail_url VARCHAR(500);
            RAISE NOTICE 'Added thumbnail_url column to books table';
        ELSE
            RAISE NOTICE 'thumbnail_url column already exists';
        END IF;
    END \$\$;
"

if [ $? -eq 0 ]; then
    echo "✅ Successfully added thumbnail_url column!"
    echo ""
    echo "🔄 Restarting application to apply changes..."
    docker compose restart library-app
    
    echo "⏳ Waiting for application to restart..."
    sleep 10
    
    # Test if the app is working
    if docker compose exec -T library-app curl -f http://localhost:5000/health >/dev/null 2>&1; then
        echo "✅ Application is running successfully!"
        echo ""
        echo "🎉 Quick fix completed! Your application should now work properly."
        echo ""
        echo "📋 Next time you update from GitHub, use:"
        echo "   ./scripts/deploy-cloudflare-enhanced.sh upgrade"
    else
        echo "⚠️  Application may need more time to start. Check with:"
        echo "   docker compose logs library-app"
    fi
else
    echo "❌ Failed to add column. Please check the database connection."
    echo "📋 Debugging commands:"
    echo "   docker compose logs library-db"
    echo "   docker compose exec library-db psql -U libraryuser library"
fi
