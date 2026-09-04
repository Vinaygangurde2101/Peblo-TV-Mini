from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from pydantic import BaseModel

from app.core.config import settings
from app.models.user import UserRole


class TokenPayload(BaseModel):
    sub: str  # User ID
    email: str
    role: UserRole
    exp: datetime


def create_access_token(user_id: str, email: str, role: UserRole, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "role": role.value,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        email: Optional[str] = payload.get("email")
        role_str: Optional[str] = payload.get("role")
        exp_timestamp = payload.get("exp")

        if not user_id or not email or not role_str or exp_timestamp is None:
            return None

        exp_dt = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        return TokenPayload(
            sub=user_id,
            email=email,
            role=UserRole(role_str),
            exp=exp_dt
        )
    except (JWTError, ValueError):
        return None
