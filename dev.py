#!/usr/bin/env python3
"""
Development helper script for Library Management System
Use this for local development instead of Windows batch files
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command"""
    try:
        print(f"🔧 {description}")
        result = subprocess.run(command, shell=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def setup_dev_environment():
    """Set up development environment"""
    print("🔧 Setting up development environment...")
    
    # Check if virtual environment exists
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            return False
    
    # Activate and install dependencies
    if os.name == "nt":
        pip_cmd = ".venv\\Scripts\\pip"
        python_cmd = ".venv\\Scripts\\python"
    else:
        pip_cmd = ".venv/bin/pip"
        python_cmd = ".venv/bin/python"
    
    print("📦 Installing dependencies...")
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing requirements"):
        return False
    
    print("🗃️ Initializing database...")
    if not run_command(f"{python_cmd} scripts/init_db.py", "Setting up database"):
        return False
    
    print("✅ Development environment ready!")
    return True

def run_app(mode="http", port=5000, debug=False):
    """Run the application"""
    cmd = f"python main.py --port {port}"
    
    if mode == "https":
        cmd += " --https"
    
    if debug:
        cmd += " --debug"
    
    print(f"🚀 Starting application in {mode.upper()} mode on port {port}")
    run_command(cmd, "Starting Flask application")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python dev.py [command] [options]")
        print("\nCommands:")
        print("  setup         - Set up development environment")
        print("  run           - Run application (HTTP)")
        print("  run-https     - Run application (HTTPS)")
        print("  run-debug     - Run application (debug mode)")
        print("  test          - Run tests")
        print("  docker-build  - Build Docker image")
        print("  docker-run    - Run Docker container")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        setup_dev_environment()
    elif command == "run":
        run_app()
    elif command == "run-https":
        run_app(mode="https")
    elif command == "run-debug":
        run_app(debug=True)
    elif command == "test":
        run_command("python -m pytest tests/", "Running tests")
    elif command == "docker-build":
        run_command("docker build -t library-management .", "Building Docker image")
    elif command == "docker-run":
        run_command("docker run -d -p 5000:5000 --name library-app library-management", "Running Docker container")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
