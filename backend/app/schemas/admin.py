from pydantic import BaseModel


class SiteSettingsResponse(BaseModel):
    site_name: str | None = None
    maintenance_mode: bool = False


class SiteSettingsUpdate(BaseModel):
    site_name: str | None = None
    maintenance_mode: bool | None = None


class UserListResponse(BaseModel):
    id: int
    email: str
    name: str | None
    is_admin: bool
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class UserUpdateBody(BaseModel):
    is_admin: bool | None = None
    is_active: bool | None = None
