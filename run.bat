@echo off
echo Starting Library Management System (HTTP)...

:: Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Check if database exists, if not, initialize it
if not exist "library.db" (
    echo Database not found. Initializing...
    python init_db.py
)

:: Start the Flask application
echo Starting Flask development server (HTTP)...
echo.
echo The application will be available at:
echo http://localhost:5000
echo.
echo For HTTPS testing, use: run_https.bat
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py
