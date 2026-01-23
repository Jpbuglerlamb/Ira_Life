# auth/tokens.py

import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets

# -------------------------
# Configuration
# -------------------------
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(64)
ALGORITHM = "HS256"

# Default short-term session token: 1 day
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Optional long-lived token (stay logged in): 30 days
LONG_TOKEN_EXPIRE_DAYS = 30

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------
# Password Utilities
# -------------------------
def hash_password(pw: str) -> str:
    return pwd.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return pwd.verify(pw, hashed)

# -------------------------
# Token Utilities
# -------------------------
def create_token(username: str, long_lived: bool = False) -> str:
    expire = datetime.utcnow() + (
        timedelta(days=LONG_TOKEN_EXPIRE_DAYS) if long_lived else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None