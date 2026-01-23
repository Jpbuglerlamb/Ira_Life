from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class UpdateProfileRequest(BaseModel):
    username: str
    fullName: str
    preferences: str