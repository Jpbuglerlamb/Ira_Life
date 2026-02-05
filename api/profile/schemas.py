# api/profile/schemas.py
from pydantic import BaseModel
from typing import Optional

class UpdateProfileRequest(BaseModel):
    fullName: str = ""
    email: str = ""
    aiPersonality: str = ""
    preferences: str = ""
    notificationsEnabled: bool = True

class ProfileResponse(BaseModel):
    fullName: str
    email: str
    aiPersonality: str
    preferences: str
    notificationsEnabled: bool
