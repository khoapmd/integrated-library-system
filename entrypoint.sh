#!/bin/bash
set -e

echo "🚀 Starting Library Management System..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if python -c "from app import app, db; app.app_context().push(); db.session.execute('SELECT 1'); print('✅ Database connection successful')"; then
        break
    else
        retry_count=$((retry_count + 1))
        echo "⏳ Database not ready, retrying... ($retry_count/$max_retries)"
        sleep 2
    fi
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ Failed to connect to database after $max_retries attempts"
    exit 1
fi

# Initialize database schema
echo "🔧 Initializing database schema..."
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database schema initialized')"

# Start the application with Gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn --config gunicorn.conf.py app:app
