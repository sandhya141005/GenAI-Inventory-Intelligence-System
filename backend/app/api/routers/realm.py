import random
import string

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_owner
from app.db.session import get_db
from app.models.analytics_data import Store
from app.models.user import STORE_MANAGER, Realm, User


router = APIRouter(prefix="/realm", tags=["realm"])


class AssignStoreRequest(BaseModel):
    store_id: int | None


def _generate_join_code(db: Session) -> str:
    for _ in range(25):
        code = "".join(random.choice(string.digits) for _ in range(4))
        if not db.scalar(select(Realm).where(Realm.join_code == code)):
            return code
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not allocate a realm join code")


@router.get("/settings")
def settings(owner: User = Depends(require_owner), db: Session = Depends(get_db)) -> dict:
    realm = db.get(Realm, owner.realm_id)
    if not realm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Realm not found")

    managers = db.scalars(
        select(User)
        .where(User.realm_id == realm.id, User.role == STORE_MANAGER, User.is_active.is_(True))
        .order_by(User.created_at.desc())
    ).all()
    stores = db.scalars(select(Store).where(Store.realm_id == realm.id).order_by(Store.name)).all()

    return {
        "realm": {
            "id": realm.id,
            "name": realm.name,
            "industry_tag": realm.industry_tag,
            "join_code": realm.join_code,
            "created_at": realm.created_at.isoformat() if realm.created_at else None,
        },
        "stores": [
            {"id": store.id, "name": store.name, "city": store.city, "region": store.region}
            for store in stores
        ],
        "managers": [
            {
                "id": manager.id,
                "full_name": manager.full_name,
                "email": manager.email,
                "assigned_store_id": manager.assigned_store_id,
                "assigned_store_name": manager.assigned_store.name if manager.assigned_store else None,
                "created_at": manager.created_at.isoformat() if manager.created_at else None,
            }
            for manager in managers
        ],
    }


@router.patch("/managers/{manager_id}/store")
def assign_store(
    manager_id: int,
    payload: AssignStoreRequest,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
) -> dict:
    manager = db.get(User, manager_id)
    if not manager or manager.realm_id != owner.realm_id or manager.role != STORE_MANAGER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store manager not found")
    if payload.store_id is not None:
        store = db.get(Store, payload.store_id)
        if not store or store.realm_id != owner.realm_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Store is outside this realm")
    manager.assigned_store_id = payload.store_id
    db.commit()
    db.refresh(manager)
    return {"ok": True, "assigned_store_id": manager.assigned_store_id}


@router.delete("/managers/{manager_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_manager(manager_id: int, owner: User = Depends(require_owner), db: Session = Depends(get_db)) -> None:
    manager = db.get(User, manager_id)
    if not manager or manager.realm_id != owner.realm_id or manager.role != STORE_MANAGER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store manager not found")
    manager.realm_id = None
    manager.role = None
    manager.assigned_store_id = None
    db.commit()


@router.post("/regenerate-code")
def regenerate_code(owner: User = Depends(require_owner), db: Session = Depends(get_db)) -> dict:
    realm = db.get(Realm, owner.realm_id)
    if not realm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Realm not found")
    realm.join_code = _generate_join_code(db)
    db.commit()
    db.refresh(realm)
    return {"join_code": realm.join_code}
