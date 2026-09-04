from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    email: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: UserRole
    full_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
