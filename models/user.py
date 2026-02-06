# models/user.py
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str = Field(..., min_length=1)
