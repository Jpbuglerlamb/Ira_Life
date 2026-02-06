# auth/tokens.py

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

# IMPORTANT:
# Set SECRET_KEY in your Render environment variables.
# If you fall back to a random secret, tokens will break on every deploy/restart.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. Add SECRET_KEY to your environment (Render dashboard) "
        "to keep JWT tokens valid across restarts."
    )

ALGORITHM = "HS256"

# Default short-term session token: 1 day
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))

# Optional long-lived token (stay logged in): 30 days
LONG_TOKEN_EXPIRE_DAYS = int(os.getenv("LONG_TOKEN_EXPIRE_DAYS", "30"))

pwd = CryptContext(schemes=["argon2"], deprecated="auto")


# -------------------------------------------------------------------
# Password Utilities
# -------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    if password is None or password == "":
        raise ValueError("Password required")
    return pwd.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    if not password or not hashed:
        return False
    try:
        return pwd.verify(password, hashed)
    except Exception:
        # If the hash is malformed or the scheme changed, don't crash auth routes.
        return False


# -------------------------------------------------------------------
# Token Utilities
# -------------------------------------------------------------------

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_token(username: str, long_lived: bool = False) -> str:
    """
    Create a JWT access token.
    'sub' holds the username, 'exp' is the expiry datetime (UTC).
    """
    if not username:
        raise ValueError("username required")

    expire = _utcnow() + (
        timedelta(days=LONG_TOKEN_EXPIRE_DAYS)
        if long_lived
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload: Dict[str, Any] = {
        "sub": username,
        "exp": expire,
        "iat": _utcnow(),
        "type": "access",
        "ll": bool(long_lived),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a JWT token. Returns payload dict or None if invalid/expired."""
    if not token:
        return None
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

