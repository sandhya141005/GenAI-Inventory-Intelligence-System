"""
Verify demo setup is complete
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models.analytics_data import Product, Store, Sale, Transfer, WarehouseStock
from app.models.user import User

def verify_setup():
    """Verify all data is present"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("🔍 VERIFYING DEMO SETUP")
        print("=" * 60)
        print()
        
        # Check each table
        checks = [
            ("Products", Product, 56),
            ("Stores", Store, 10),
            ("Warehouse Stock", WarehouseStock, 56),
            ("Sales", Sale, 8000, "~9000"),
            ("Transfers", Transfer, 7),
            ("Users", User, 1, "1+"),
        ]
        
        all_pass = True
        
        for name, model, expected, display in [(c[0], c[1], c[2], c[3] if len(c) > 3 else None) for c in checks]:
            count = db.query(model).count()
            display_expected = display if display else str(expected)
            
            if isinstance(expected, int):
                if name in ["Sales"]:
                    # Sales can vary, just check > threshold
                    status = "✅" if count >= expected else "❌"
                    passed = count >= expected
                elif name in ["Users"]:
                    # Users should be at least 1
                    status = "✅" if count >= expected else "❌"
                    passed = count >= expected
                else:
                    # Exact match
                    status = "✅" if count == expected else "❌"
                    passed = count == expected
                
                all_pass = all_pass and passed
                print(f"{status} {name:20} Count: {count:6}  Expected: {display_expected}")
        
        print()
        print("=" * 60)
        
        if all_pass:
            print("✅ ALL CHECKS PASSED - SETUP COMPLETE!")
            print("=" * 60)
            print()
            print("🎯 Next Steps:")
            print("   1. Start backend: uvicorn app.main:app --reload")
            print("   2. Start frontend: npm run dev")
            if db.query(User).count() == 0:
                print("   3. Create user at http://localhost:3000/signup")
                print("      Email: demo@mckinsey.com")
                print("      Password: demo1234")
            else:
                print("   3. Login at http://localhost:3000")
                print("      Email: demo@mckinsey.com")
                print("      Password: demo1234")
            print()
            return True
        else:
            print("❌ SOME CHECKS FAILED")
            print("=" * 60)
            print()
            print("🔧 Troubleshooting:")
            
            if db.query(Product).count() == 0:
                print("   • No products found")
                print("     Run: python scripts/generate_demo_data_simple.py")
            
            if db.query(User).count() == 0:
                print("   • No users found")
                print("     Create user at http://localhost:3000/signup")
                print("     OR via API: POST http://localhost:8000/api/auth/signup")
            
            print()
            return False
            
    except Exception as e:
        print()
        print(f"❌ Error during verification: {e}")
        print()
        print("🔧 Possible Issues:")
        print("   • Database not running")
        print("   • Wrong DATABASE_URL in .env")
        print("   • Migrations not applied: alembic upgrade head")
        print()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = verify_setup()
    sys.exit(0 if success else 1)
