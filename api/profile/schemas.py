#api/profile/schemas.py
from pydantic import BaseModel

class UpdateProfileRequest(BaseModel):
    fullName: str
    email: str
    aiPersonality: str
    notificationsEnabled: bool = True

class ProfileResponse(BaseModel):
    fullName: str
    preferences: str

class UpdateProfileRequest(BaseModel):
    fullName: str
    preferences: str