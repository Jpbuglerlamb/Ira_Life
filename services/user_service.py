from fastapi import HTTPException
from typing import Optional, Dict, Any

from auth.tokens import hash_password
from models.user import UserModel
from db.session import get_db


class UserService:
    @staticmethod
    def get_user(username: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        return db.get_user_by_username(username)

    @staticmethod
    def create_user(username: str, password: str) -> Dict[str, Any]:
        if not username:
            raise HTTPException(status_code=400, detail="Username required")
        if not password:
            raise HTTPException(status_code=400, detail="Password required")

        db = get_db()

        if db.get_user_by_username(username):
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = hash_password(password)

        user = db.create_user(
            username=username,
            hashed_password=hashed_password
        )

        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")

        return user