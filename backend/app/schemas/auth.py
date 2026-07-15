from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, min_length=2, max_length=255)
    industry_tag: str | None = Field(default=None, min_length=2, max_length=120)
    realm_action: Literal["create", "join"]
    join_code: str | None = Field(default=None, min_length=4, max_length=4)


class UserLogin(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserRead(BaseModel):
    id: int
    # Allow local-domain demo accounts (e.g. *@stocklens.local) in API responses.
    email: str
    full_name: str | None
    is_active: bool
    realm_id: int | None = None
    role: str | None = None
    assigned_store_id: int | None = None
    assigned_store_name: str | None = None
    realm_name: str | None = None
    industry_tag: str | None = None

    model_config = {"from_attributes": True}
