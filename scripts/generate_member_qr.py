#!/usr/bin/env python3
"""
Generate QR codes for library members
This script creates QR codes that can be used on member ID cards for quick scanning during checkout.
"""

import json
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
from models import db, Member
from app import app

def generate_member_qr_data(member):
    """Generate QR code data for a member"""
    return json.dumps({
        'type': 'library_member',
        'member_id': member.member_id,
        'employee_code': member.employee_code,
        'first_name': member.first_name,
        'last_name': member.last_name,
        'generated_at': datetime.now().isoformat()
    })

def generate_large_employee_qr(employee_code, save_path=None):
    """Generate a large, easily scannable QR code with just the employee code"""
    
    # Create QR code with larger settings for better scanning
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
        box_size=15,  # Larger box size for better scanning
        border=4,
    )
    qr.add_data(employee_code)
    qr.make(fit=True)
    
    # Create QR code image with high resolution
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Make it even larger for phone scanning
    large_size = 500  # 500x500 pixels for easy scanning
    qr_img_large = qr_img.resize((large_size, large_size), Image.NEAREST)
    
    if save_path:
        qr_img_large.save(save_path)
        print(f"✅ Employee QR code saved: {save_path}")
        print(f"   Employee Code: {employee_code}")
    
    return qr_img_large

def generate_test_employee_qrs():
    """Generate large QR codes for testing with existing employee codes"""
    
    # Create output directory
    output_dir = "test_employee_qrs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with app.app_context():
        # Get all active members and their employee codes
        members = Member.query.filter_by(status='active').all()
        
        print(f"🎯 Found {len(members)} active members")
        
        for member in members:
            if member.employee_code:
                filename = f"employee_{member.employee_code}.png"
                filepath = os.path.join(output_dir, filename)
                
                try:
                    generate_large_employee_qr(member.employee_code, filepath)
                    print(f"✅ Generated QR for: {member.first_name} {member.last_name} (Employee: {member.employee_code})")
                except Exception as e:
                    print(f"❌ Error generating QR for employee {member.employee_code}: {e}")
        
        # Also generate some test employee codes
        test_codes = ["EMP001", "EMP002", "12345", "525552"]  # Include the existing employee code
        for code in test_codes:
            filename = f"test_employee_{code}.png"
            filepath = os.path.join(output_dir, filename)
            generate_large_employee_qr(code, filepath)
        
        print(f"\n🎉 Employee QR codes saved in '{output_dir}' directory")
        print("These large QR codes should be much easier to scan with a phone!")

def create_member_qr_code(member, save_path=None):
    """Create a QR code for a member with their information"""
    
    # For company cards, we just need the employee code as a simple QR
    employee_code = member.employee_code or member.member_id
    
    return generate_large_employee_qr(employee_code, save_path), employee_code

def generate_all_member_cards():
    """Generate simple employee QR codes for testing"""
    return generate_test_employee_qrs()

def generate_sample_member_qr():
    """Generate large, easily scannable QR codes for testing"""
    
    # Create different types of test QR codes
    test_codes = [
        "525552",  # Existing employee code from database
        "EMP001",  # Sample employee code
        "12345",   # Simple numeric code
        "STAFF789" # Another format
    ]
    
    for code in test_codes:
        filename = f"large_test_{code}.png"
        qr_img = generate_large_employee_qr(code, filename)
        print(f"✅ Large test QR code saved: {filename}")
        print(f"   Contains: {code}")
        print(f"   Size: 500x500 pixels for easy scanning")
    
    print("\n📱 These QR codes are optimized for phone camera scanning!")
    print("💡 Tip: The company employee cards should contain similar simple employee codes")

if __name__ == "__main__":
    print("🏷️ Employee QR Code Generator for Library System")
    print("=" * 50)
    print("This generates large, scannable QR codes containing employee codes")
    print("that work with your existing company employee cards.")
    print()
    
    choice = input("Generate: (1) Test employee QRs, (2) Large sample QRs, or (3) Both? [1/2/3]: ").strip()
    
    if choice in ['1', '3']:
        generate_test_employee_qrs()
    
    if choice in ['2', '3']:
        generate_sample_member_qr()
    
    print("\n✨ Done!")
    print("📋 Next steps:")
    print("1. Test scanning the generated QR codes with your phone")
    print("2. Make sure your company employee cards have similar simple employee codes")
    print("3. The library system will detect employee codes and auto-select members")
