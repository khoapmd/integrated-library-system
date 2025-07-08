#!/usr/bin/env python3
"""
Test script for circulation scanner functionality
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_circulation_endpoints():
    """Test circulation API endpoints"""
    print("🔍 Testing Circulation API Endpoints")
    print("=" * 50)
    
    # Test 1: Get book status
    print("\n1. Testing book status endpoint...")
    try:
        # First get a book UUID from books API
        books_response = requests.get(f"{BASE_URL}/api/books")
        if books_response.status_code == 200:
            books_data = books_response.json()
            if books_data.get('books') and len(books_data['books']) > 0:
                test_book = books_data['books'][0]
                book_uuid = test_book.get('uuid')
                
                if book_uuid:
                    status_response = requests.get(f"{BASE_URL}/api/circulation/status/{book_uuid}")
                    print(f"   Status Code: {status_response.status_code}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   ✅ Book status retrieved: {status_data.get('success')}")
                        if status_data.get('book'):
                            print(f"   📚 Book: {status_data['book'].get('title')}")
                    else:
                        print(f"   ❌ Error: {status_response.text}")
                else:
                    print("   ⚠️  No UUID found in book data")
            else:
                print("   ⚠️  No books found")
        else:
            print(f"   ❌ Failed to get books: {books_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing book status: {e}")
    
    # Test 2: Get members
    print("\n2. Testing members endpoint...")
    try:
        members_response = requests.get(f"{BASE_URL}/api/members")
        print(f"   Status Code: {members_response.status_code}")
        if members_response.status_code == 200:
            members_data = members_response.json()
            print(f"   ✅ Members retrieved: {members_data.get('success')}")
            if members_data.get('members'):
                print(f"   👥 Total members: {len(members_data['members'])}")
        else:
            print(f"   ❌ Error: {members_response.text}")
    except Exception as e:
        print(f"   ❌ Error testing members: {e}")
    
    # Test 3: Get transactions
    print("\n3. Testing transactions endpoint...")
    try:
        transactions_response = requests.get(f"{BASE_URL}/api/transactions")
        print(f"   Status Code: {transactions_response.status_code}")
        if transactions_response.status_code == 200:
            transactions_data = transactions_response.json()
            print(f"   ✅ Transactions retrieved successfully")
            print(f"   📊 Total transactions: {len(transactions_data) if isinstance(transactions_data, list) else 'Unknown'}")
        else:
            print(f"   ❌ Error: {transactions_response.text}")
    except Exception as e:
        print(f"   ❌ Error testing transactions: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Circulation endpoint tests completed!")

def test_server_connection():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == '__main__':
    print("🚀 Testing Circulation Scanner Functionality")
    print("=" * 60)
    
    # Check if server is running
    if not test_server_connection():
        print("❌ Server is not running on http://localhost:5000")
        print("Please start the Flask application first.")
        sys.exit(1)
    
    print("✅ Server is running!")
    
    # Run tests
    test_circulation_endpoints()
