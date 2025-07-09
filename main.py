#!/usr/bin/env python3
"""
Library Management System
Main application entry point

Usage:
    python main.py                  # Run with HTTP
    python main.py --https          # Run with HTTPS
    python main.py --port 8080      # Run on custom port
    python main.py --debug          # Run in debug mode
"""

import sys
import os
import argparse

from app import app, db

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Library Management System')
    parser.add_argument('--https', action='store_true', help='Run with HTTPS')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    return parser.parse_args()

def main():
    """Main application entry point"""
    args = parse_arguments()
    
    # Initialize database
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")
    
    # Configure SSL if HTTPS is requested
    ssl_context = None
    if args.https:
        try:
            import ssl
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain('cert.pem', 'key.pem')
            print(f"🔒 HTTPS enabled on https://{args.host}:{args.port}")
        except FileNotFoundError:
            print("❌ SSL certificate files not found. Run 'python scripts/generate_ssl_certs.py' first.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ SSL setup failed: {e}")
            sys.exit(1)
    else:
        print(f"🌐 HTTP server starting on http://{args.host}:{args.port}")
    
    # Start the application
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            ssl_context=ssl_context
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
