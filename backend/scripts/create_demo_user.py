"""
Create demo user directly in database
Run after generate_demo_data_simple.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_demo_user():
    """Create demo user"""
    db = SessionLocal()
    
    try:
        demo_email = "demo@mckinsey.com"
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == demo_email).first()
        
        if existing_user:
            print(f"✅ Demo user already exists: {demo_email}")
            print(f"   User ID: {existing_user.id}")
            print(f"   Name: {existing_user.full_name}")
            print(f"   Active: {existing_user.is_active}")
            return
        
        # Create new user
        user = User(
            email=demo_email,
            full_name="McKinsey Demo User",
            hashed_password=hash_password("demo1234"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("=" * 60)
        print("✅ DEMO USER CREATED SUCCESSFULLY")
        print("=" * 60)
        print(f"Email: {demo_email}")
        print(f"Password: demo1234")
        print(f"User ID: {user.id}")
        print(f"Full Name: {user.full_name}")
        print("=" * 60)
        print("\n🎯 Next Steps:")
        print("   1. Start backend: uvicorn app.main:app --reload")
        print("   2. Start frontend: npm run dev")
        print("   3. Login at http://localhost:3000")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating demo user: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_user()
