#!/usr/bin/env python3
"""
Setup script for Library Management System
Handles database initialization and basic configuration for Docker deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    try:
        print(f"🔧 {description}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True

def initialize_database():
    """Initialize the database"""
    return run_command(
        "python scripts/init_db.py",
        "Initializing database..."
    )

def generate_ssl_certificates():
    """Generate SSL certificates for HTTPS"""
    if os.path.exists("cert.pem") and os.path.exists("key.pem"):
        print("✅ SSL certificates already exist")
        return True
    
    return run_command(
        "python scripts/generate_ssl_certs.py",
        "Generating SSL certificates..."
    )

def create_directories():
    """Create necessary directories"""
    directories = [
        "instance",
        "member_cards",
        "uploads",
        "data",
        "logs"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")

def main():
    """Main setup function for Docker deployment"""
    print("=" * 60)
    print("📚 LIBRARY MANAGEMENT SYSTEM SETUP")
    print("🐳 Docker Deployment Configuration")
    print("=" * 60)
    
    # Step 1: Check Python version
    print("\n1️⃣ Checking Python version...")
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Create directories
    print("\n2️⃣ Creating directories...")
    create_directories()
    
    # Step 3: Initialize database
    print("\n3️⃣ Setting up database...")
    if not initialize_database():
        print("   ⚠️ Database initialization failed, but you can run it manually later")
    
    # Step 4: Generate SSL certificates
    print("\n4️⃣ Setting up SSL certificates...")
    if not generate_ssl_certificates():
        print("   ⚠️ SSL certificate generation failed, but you can run it manually later")
    
    # Final instructions
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("\n� For Docker deployment:")
    print("   1. Build Docker image: docker build -t library-management .")
    print("   2. Run container: docker run -p 5000:5000 library-management")
    print("\n🚀 For local development:")
    print("   python main.py")
    print("\n🌐 Then visit: http://localhost:5000")
    print("🔒 For HTTPS: python main.py --https")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
