"""
Create or repair demo users directly in the active database.

This script is intentionally idempotent: rerun it any time the demo login stops
working after migrations, reseeding, or local database resets.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.analytics_data import Store
from app.models.user import Realm, STORE_MANAGER, WAREHOUSE_OWNER, User


DEMO_PASSWORD = "demo1234"


def upsert_user(
    db,
    *,
    email: str,
    full_name: str,
    realm_id: int,
    role: str,
    assigned_store_id: int | None = None,
) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
    user.full_name = full_name
    user.hashed_password = hash_password(DEMO_PASSWORD)
    user.is_active = True
    user.realm_id = realm_id
    user.role = role
    user.assigned_store_id = assigned_store_id
    db.flush()
    return user


def create_demo_user() -> None:
    db = SessionLocal()
    try:
        realm = db.query(Realm).filter(Realm.join_code == "8341").first()
        if not realm:
            realm = Realm(
                name="StockLens Automotive Demo",
                industry_tag="Automotive Parts",
                join_code="8341",
            )
            db.add(realm)
            db.flush()

        owner = upsert_user(
            db,
            email="demo@mckinsey.com",
            full_name="McKinsey Demo User",
            realm_id=realm.id,
            role=WAREHOUSE_OWNER,
        )
        realm.owner_user_id = owner.id

        stores = db.query(Store).filter(Store.realm_id == realm.id).order_by(Store.id).all()
        assigned_stores = [store for store in stores if store.store_type != "hub"] or stores
        if assigned_stores:
            upsert_user(
                db,
                email="chennai.manager@stocklens.local",
                full_name="Chennai Store Manager",
                realm_id=realm.id,
                role=STORE_MANAGER,
                assigned_store_id=assigned_stores[min(4, len(assigned_stores) - 1)].id,
            )
            upsert_user(
                db,
                email="mumbai.manager@stocklens.local",
                full_name="Mumbai Store Manager",
                realm_id=realm.id,
                role=STORE_MANAGER,
                assigned_store_id=assigned_stores[0].id,
            )

        upsert_user(
            db,
            email="unassigned.manager@stocklens.local",
            full_name="Unassigned Store Manager",
            realm_id=realm.id,
            role=STORE_MANAGER,
            assigned_store_id=None,
        )

        db.commit()
        print("Demo users are ready.")
        print(f"Owner: demo@mckinsey.com / {DEMO_PASSWORD}")
        print(f"Join code: {realm.join_code}")
        print(f"Managers use password: {DEMO_PASSWORD}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_user()
