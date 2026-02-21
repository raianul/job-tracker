from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    name: str | None = None
    avatar_url: str | None = None
    provider: str
    is_admin: bool = False
    is_active: bool = True


class UserCreate(UserBase):
    provider_id: str


class UserInDB(UserBase):
    id: int
    provider_id: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: str
    name: str | None
    avatar_url: str | None
    provider: str
    is_admin: bool
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
