from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.auth.jwt import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency resolving the current authenticated user from Bearer token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == payload.sub).first()
    if user is None:
        raise credentials_exception

    return user


def require_roles(allowed_roles: List[UserRole]):
    """
    Higher-order dependency enforcing Role-Based Access Control (RBAC).
    Returns HTTP 403 Forbidden if user's role is not in allowed_roles.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required role: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user

    return role_checker


# Convenience dependency shorthands
get_current_admin = require_roles([UserRole.ADMIN])
get_current_editor_or_admin = require_roles([UserRole.EDITOR, UserRole.ADMIN])
