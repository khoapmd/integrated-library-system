#!/usr/bin/env python3
"""
Test script to verify the enhanced ISBN lookup fallback system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ISBNScanner

def test_isbn_fallback():
    """Test the ISBN lookup with fallback services"""
    
    # Create scanner instance
    scanner = ISBNScanner()
    
    print("=" * 60)
    print("Testing Enhanced ISBN Lookup with Fallback Services")
    print("=" * 60)
    
    # Test with a well-known ISBN
    test_isbn = "9780134685991"  # Effective Java by Joshua Bloch
    print(f"\nTesting ISBN: {test_isbn}")
    print("-" * 40)
    
    try:
        book_info = scanner.get_book_info_by_isbn(test_isbn)
        
        if book_info:
            print("✅ SUCCESS! Book information found:")
            print(f"   Title: {book_info.get('title', 'N/A')}")
            print(f"   Author: {book_info.get('author', 'N/A')}")
            print(f"   Publisher: {book_info.get('publisher', 'N/A')}")
            print(f"   Source: {book_info.get('source', 'N/A')}")
            print(f"   ISBN: {book_info.get('isbn', 'N/A')}")
        else:
            print("❌ No book information found")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_isbn_fallback()
