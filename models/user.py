# models/user.py
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str = Field(..., min_length=1)

class UpdateProfileRequest(BaseModel):
    username: str
    fullName: str
    preferences: str