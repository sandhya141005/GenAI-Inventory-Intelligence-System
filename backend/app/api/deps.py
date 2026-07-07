from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import STORE_MANAGER, WAREHOUSE_OWNER, User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        user_id = int(decode_token(token, expected_type="access"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials") from exc

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user


@dataclass(frozen=True)
class AccessScope:
    realm_id: int
    role: str
    assigned_store_id: int | None = None

    @property
    def is_owner(self) -> bool:
        return self.role == WAREHOUSE_OWNER

    @property
    def is_store_manager(self) -> bool:
        return self.role == STORE_MANAGER

    @property
    def requires_store_assignment(self) -> bool:
        return self.is_store_manager and self.assigned_store_id is None


def get_access_scope(current_user: User = Depends(get_current_user)) -> AccessScope:
    if current_user.realm_id is None or current_user.role not in {WAREHOUSE_OWNER, STORE_MANAGER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not connected to a realm")
    return AccessScope(
        realm_id=current_user.realm_id,
        role=current_user.role,
        assigned_store_id=current_user.assigned_store_id,
    )


def require_owner(current_user: User = Depends(get_current_user)) -> User:
    if current_user.realm_id is None or current_user.role != WAREHOUSE_OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Warehouse Owner access required")
    return current_user
