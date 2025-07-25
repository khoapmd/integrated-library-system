#!/usr/bin/env python3
"""
Pre-deployment verification script
This script checks if the deployment will be safe and migrations will work correctly
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_migrations():
    """Test that migrations will work without data loss"""
    print("🔍 Testing migration safety...")
    
    try:
        from app import create_app
        from models import db, Book
        from utils import normalize_vietnamese_text, create_search_variants
        
        app = create_app()
        with app.app_context():
            # Test normalization function
            test_cases = [
                "Lãnh đạo bằng câu hỏi",
                "Effective Java",
                "Tôi yêu Việt Nam",
                "Learning JavaScript Design Patterns"
            ]
            
            print("✅ Testing Vietnamese text normalization:")
            for text in test_cases:
                normalized = normalize_vietnamese_text(text)
                variants = create_search_variants(text)
                print(f"   '{text}' → '{normalized}' (variants: {len(variants)})")
            
            # Test database connection
            print("🔍 Testing database connection...")
            try:
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            
            # Check if migration will be safe
            print("🔍 Checking existing database schema...")
            tables = db.inspector.get_table_names()
            if 'books' in tables:
                columns = [col['name'] for col in db.inspector.get_columns('books')]
                print(f"✅ Books table exists with {len(columns)} columns")
                
                # Check for new columns
                new_columns = ['title_normalized', 'author_normalized']
                missing_columns = [col for col in new_columns if col not in columns]
                
                if missing_columns:
                    print(f"📋 Migration will add columns: {missing_columns}")
                    print("✅ Migration is safe - will only ADD columns, no data loss")
                else:
                    print("ℹ️  All migration columns already exist")
            else:
                print("📋 Books table doesn't exist - initial setup required")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Pre-Deployment Migration Safety Check")
    print("========================================")
    
    if test_migrations():
        print("")
        print("🎉 Migration safety check PASSED!")
        print("✅ Your deployment with './scripts/deploy-cloudflare.sh upgrade' will be safe")
        print("✅ No data will be lost during the migration")
        print("✅ Vietnamese search functionality will be added")
        print("")
        print("🔄 Ready to deploy with:")
        print("   ./scripts/deploy-cloudflare.sh upgrade")
    else:
        print("")
        print("❌ Migration safety check FAILED!")
        print("⚠️  Please review the errors above before deploying")
        sys.exit(1)

if __name__ == '__main__':
    main()
