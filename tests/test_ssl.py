#!/usr/bin/env python3
"""
Test script to verify HTTP and HTTPS functionality
"""

import requests
import time
import subprocess
import sys
import threading
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings for testing with self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_server(url, protocol):
    """Test if the server is responding"""
    try:
        # For HTTPS, we need to disable SSL verification since we're using self-signed certificates
        verify_ssl = False if protocol == "HTTPS" else True
        
        response = requests.get(url, timeout=5, verify=verify_ssl)
        if response.status_code == 200:
            print(f"✓ {protocol} server is running and accessible at {url}")
            return True
        else:
            print(f"✗ {protocol} server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ {protocol} server connection failed: {e}")
        return False

def run_server_test(command, protocol, url):
    """Run server and test connectivity"""
    print(f"\n--- Testing {protocol} Server ---")
    
    # Start server in background
    try:
        process = subprocess.Popen(
            command, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Wait for server to start
        print(f"Starting {protocol} server...")
        time.sleep(3)
        
        # Test connectivity
        success = test_server(url, protocol)
        
        # Stop server
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            
        return success
        
    except Exception as e:
        print(f"Error running {protocol} server: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Library Management System HTTP/HTTPS functionality\n")
    
    python_executable = "C:/Python313/python.exe"
    
    # Test HTTP
    http_success = run_server_test(
        f"{python_executable} app.py",
        "HTTP",
        "http://localhost:5000"
    )
    
    # Test HTTPS
    https_success = run_server_test(
        f"{python_executable} app.py --https",
        "HTTPS", 
        "https://localhost:5000"
    )
    
    # Summary
    print("\n--- Test Summary ---")
    print(f"HTTP:  {'PASS' if http_success else 'FAIL'}")
    print(f"HTTPS: {'PASS' if https_success else 'FAIL'}")
    
    if http_success and https_success:
        print("\n✓ All tests passed! Both HTTP and HTTPS are working correctly.")
        return 0
    else:
        print("\n✗ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
