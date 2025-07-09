#!/usr/bin/env python3
"""
Test API endpoints to see if data can be retrieved via the web interface
"""

import requests
import json

def test_api_endpoints():
    """Test the API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("TESTING API ENDPOINTS")
    print("=" * 60)
    
    try:
        # Test books API
        print("\n📚 Testing Books API...")
        response = requests.get(f"{base_url}/api/books")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Books API working - Found {len(data.get('books', []))} books")
            if data.get('books'):
                print(f"   📖 First book: {data['books'][0].get('title', 'N/A')}")
        else:
            print(f"   ❌ Books API failed - Status: {response.status_code}")
        
        # Test members API
        print("\n👤 Testing Members API...")
        response = requests.get(f"{base_url}/api/members")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                members = data.get('members', [])
                print(f"   ✅ Members API working - Found {len(members)} members")
                if members:
                    print(f"   👥 First member: {members[0].get('first_name', 'N/A')} {members[0].get('last_name', 'N/A')}")
            else:
                print(f"   ⚠️ Members API returned error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Members API failed - Status: {response.status_code}")
        
        # Test circulation API
        print("\n🔄 Testing Circulation API...")
        response = requests.get(f"{base_url}/api/circulation/recent")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                transactions = data.get('transactions', [])
                print(f"   ✅ Circulation API working - Found {len(transactions)} transactions")
            else:
                print(f"   ⚠️ Circulation API returned error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Circulation API failed - Status: {response.status_code}")
            
    except requests.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"❌ Error testing APIs: {e}")
    
    print(f"\n" + "=" * 60)
    print("API TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_api_endpoints()
