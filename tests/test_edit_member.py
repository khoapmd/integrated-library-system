#!/usr/bin/env python3
"""
Test script to verify edit member functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_edit_member():
    """Test the edit member functionality"""
    
    # First, add a test member
    print("1. Adding a test member...")
    member_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "employee_code": "EMP123",
        "department": "NPD",
        "address": "123 Test Street",
        "membership_type": "regular",
        "max_books": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/members", json=member_data)
    if response.status_code == 201:
        result = response.json()
        if result['success']:
            member_id = result['member']['id']
            print(f"✓ Member created successfully with ID: {member_id}")
            print(f"  Member details: {result['member']['first_name']} {result['member']['last_name']}")
            print(f"  Employee Code: {result['member']['employee_code']}")
            print(f"  Department: {result['member']['department']}")
        else:
            print(f"✗ Failed to create member: {result['message']}")
            return
    else:
        print(f"✗ Failed to create member: HTTP {response.status_code}")
        return
    
    # Now test editing the member
    print(f"\n2. Editing member {member_id}...")
    updated_data = {
        "first_name": "Updated",
        "last_name": "TestUser",
        "email": "updated.test@example.com",
        "employee_code": "EMP456",
        "department": "VE",
        "address": "456 Updated Street",
        "membership_type": "premium",
        "max_books": 10
    }
    
    response = requests.put(f"{BASE_URL}/api/members/{member_id}", json=updated_data)
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✓ Member updated successfully")
            print(f"  Updated details: {result['member']['first_name']} {result['member']['last_name']}")
            print(f"  New Employee Code: {result['member']['employee_code']}")
            print(f"  New Department: {result['member']['department']}")
            print(f"  New Membership Type: {result['member']['membership_type']}")
            print(f"  New Max Books: {result['member']['max_books']}")
        else:
            print(f"✗ Failed to update member: {result['message']}")
    else:
        print(f"✗ Failed to update member: HTTP {response.status_code}")
        print(f"  Response: {response.text}")
    
    # Verify the update by fetching the member
    print(f"\n3. Verifying the update...")
    response = requests.get(f"{BASE_URL}/api/members/{member_id}")
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            member = result['member']
            print("✓ Member verification successful")
            print(f"  Name: {member['first_name']} {member['last_name']}")
            print(f"  Email: {member['email']}")
            print(f"  Employee Code: {member['employee_code']}")
            print(f"  Department: {member['department']}")
            print(f"  Membership Type: {member['membership_type']}")
            print(f"  Max Books: {member['max_books']}")
        else:
            print(f"✗ Failed to verify member: {result['message']}")
    else:
        print(f"✗ Failed to verify member: HTTP {response.status_code}")

if __name__ == "__main__":
    try:
        test_edit_member()
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to the Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"✗ Error during testing: {e}")
