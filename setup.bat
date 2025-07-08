@echo off
echo Setting up Library Management System...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH. Please install Python 3.7 or later.
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo Installing Python packages...
pip install -r requirements.txt

:: Create uploads directory
echo Creating directories...
if not exist "uploads" mkdir uploads

:: Initialize database
echo Initializing database...
python init_db.py

echo.
echo ========================================
echo Library Management System Setup Complete!
echo ========================================
echo.
echo To start the application:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run the application: python app.py
echo 3. Open your browser and go to http://localhost:5000
echo.
echo Features:
echo - QR Code generation and scanning
echo - ISBN barcode scanning
echo - Book management
echo - Member management
echo - Transaction tracking
echo.
pause
