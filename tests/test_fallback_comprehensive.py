#!/usr/bin/env python3
"""
Test script to demonstrate the ISBN fallback behavior with different scenarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ISBNScanner

def test_fallback_scenarios():
    """Test different fallback scenarios"""
    
    scanner = ISBNScanner()
    
    print("=" * 70)
    print("Testing ISBN Lookup Fallback Scenarios")
    print("=" * 70)
    
    # Test cases: (isbn, description)
    test_cases = [
        ("9780134685991", "Well-known book (should work with first service)"),
        ("9783161484100", "Example ISBN (may need fallback)"),
        ("1234567890123", "Invalid/non-existent ISBN (will use all fallbacks)"),
    ]
    
    for isbn, description in test_cases:
        print(f"\n📚 Test Case: {description}")
        print(f"   ISBN: {isbn}")
        print("-" * 50)
        
        try:
            book_info = scanner.get_book_info_by_isbn(isbn)
            
            if book_info:
                print(f"✅ Result: {book_info.get('source', 'unknown_source')}")
                print(f"   Title: {book_info.get('title', 'N/A')}")
                print(f"   Author: {book_info.get('author', 'N/A')}")
            else:
                print("❌ No book information found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("Fallback System Details:")
    print("1. Try each isbnlib service: " + str(scanner.services))
    print("2. Try isbnlib default service")
    print("3. Try Google Books API directly")
    print("4. Try Open Library API")
    print("5. Return basic placeholder info")
    print("=" * 70)

if __name__ == "__main__":
    test_fallback_scenarios()
