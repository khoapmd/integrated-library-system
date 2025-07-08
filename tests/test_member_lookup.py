#!/usr/bin/env python3
"""
Test member lookup by employee code
This script tests if we can find members by their employee codes from company QR cards.
"""

import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..') if '__file__' in globals() else '..')

from models import db, Member
from app import app
import json

def test_member_lookup():
    """Test member lookup functionality"""
    
    with app.app_context():
        # Get all members to see what employee codes we have
        members = Member.query.all()
        
        print("🏢 Current Members in Database:")
        print("=" * 50)
        
        for member in members:
            print(f"Name: {member.first_name} {member.last_name}")
            print(f"Member ID: {member.member_id}")
            print(f"Employee Code: {member.employee_code}")
            print(f"Department: {member.department}")
            print(f"Status: {member.status}")
            print("-" * 30)
        
        print(f"\n📊 Total Members: {len(members)}")
        
        # Test lookup by employee code
        if members:
            test_member = members[0]
            if test_member.employee_code:
                print(f"\n🔍 Testing lookup for employee code: {test_member.employee_code}")
                
                # Test the lookup
                found_member = Member.query.filter_by(employee_code=test_member.employee_code).first()
                if found_member:
                    print(f"✅ SUCCESS: Found {found_member.first_name} {found_member.last_name}")
                else:
                    print("❌ FAILED: Member not found")
                
                # Test what a company QR code might contain
                print(f"\n📱 Your company QR code should contain: '{test_member.employee_code}'")
                print("   When you scan it, the system will:")
                print("   1. Detect the employee code")
                print("   2. Look up the member in the database")
                print("   3. Auto-select them for checkout")
            else:
                print("⚠️  This member has no employee code set")

if __name__ == "__main__":
    print("🧪 Member Lookup Test")
    print("=" * 30)
    test_member_lookup()
    print("\n✨ Test Complete!")
    print("\n💡 Next Steps:")
    print("   1. Go to /circulation page")
    print("   2. Select 'Check Out' mode")
    print("   3. Scan your company employee QR card")
    print("   4. The member should be auto-selected!")
