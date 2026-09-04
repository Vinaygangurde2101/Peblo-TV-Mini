import bcrypt  # type: ignore # pyrefly: ignore [missing-import]


def hash_password(password: str) -> str:
    """Hashes plain text password using bcrypt."""
    # Truncate to 72 bytes if necessary per bcrypt algorithm limit
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain text password against stored bcrypt hash."""
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)
