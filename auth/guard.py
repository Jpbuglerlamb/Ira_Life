# auth/guard.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.tokens import decode_token
from jose import ExpiredSignatureError

# Use the full API path for login
oauth2 = OAuth2PasswordBearer(tokenUrl="/login")

def get_user(token: str = Depends(oauth2)) -> str:
    """
    Extract username from JWT token.

    Raises:
        HTTPException 401 if token is invalid or expired.
    """
    try:
        payload = decode_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload["sub"]
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )