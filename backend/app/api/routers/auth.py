import random
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.industries import INDUSTRY_TAGS
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import STORE_MANAGER, WAREHOUSE_OWNER, Realm, User
from app.schemas.auth import RefreshTokenRequest, TokenPair, UserCreate, UserLogin, UserRead


router = APIRouter(prefix="/auth", tags=["auth"])


def build_token_pair(user: User) -> TokenPair:
    subject = str(user.id)
    claims = {
        "realm_id": user.realm_id,
        "role": user.role,
        "assigned_store_id": user.assigned_store_id,
    }
    return TokenPair(access_token=create_access_token(subject, extra_claims=claims), refresh_token=create_refresh_token(subject))


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "realm_id": user.realm_id,
        "role": user.role,
        "assigned_store_id": user.assigned_store_id,
        "assigned_store_name": user.assigned_store.name if user.assigned_store else None,
        "realm_name": user.realm.name if user.realm else None,
        "industry_tag": user.realm.industry_tag if user.realm else None,
    }


def generate_join_code(db: Session) -> str:
    alphabet = string.digits
    for _ in range(25):
        code = "".join(random.choice(alphabet) for _ in range(4))
        if not db.scalar(select(Realm).where(Realm.join_code == code)):
            return code
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not allocate a realm join code")


@router.get("/industry-tags")
def industry_tags() -> dict:
    return {"tags": INDUSTRY_TAGS}


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> dict:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
    user = User(email=payload.email.lower(), full_name=payload.full_name, hashed_password=hash_password(payload.password))
    db.add(user)
    db.flush()

    if payload.realm_action == "create":
        if not payload.company_name:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Company name is required")
        if not payload.industry_tag:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Industry tag is required")
        if payload.industry_tag not in INDUSTRY_TAGS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported industry tag")
        realm = Realm(
            name=payload.company_name.strip(),
            industry_tag=payload.industry_tag,
            join_code=generate_join_code(db),
            owner_user_id=user.id,
        )
        db.add(realm)
        db.flush()
        user.realm_id = realm.id
        user.role = WAREHOUSE_OWNER
    else:
        if not payload.join_code:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Join code is required")
        realm = db.scalar(select(Realm).where(Realm.join_code == payload.join_code.strip()))
        if not realm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Realm join code was not found")
        user.realm_id = realm.id
        user.role = STORE_MANAGER
        user.assigned_store_id = None

    db.commit()
    db.refresh(user)
    return serialize_user(user)


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenPair:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return build_token_pair(user)


@router.post("/refresh", response_model=TokenPair)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        user_id = int(decode_token(payload.refresh_token, expected_type="refresh"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return build_token_pair(user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> dict:
    return serialize_user(current_user)
