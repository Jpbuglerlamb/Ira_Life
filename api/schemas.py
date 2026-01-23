# api/schemas.py

from pydantic import BaseModel
from typing import Optional, List


# -----------------------------
# Auth
# -----------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: Optional[bool] = False


# -----------------------------
# Chat
# -----------------------------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# -----------------------------
# Modes
# -----------------------------
class ModeRequest(BaseModel):
    mode: str


class ModesResponse(BaseModel):
    modes: List[str]


# -----------------------------
# Profile / Memory
# -----------------------------
class UpdateProfileRequest(BaseModel):
    fullName: str
    email: str
    aiPersonality: str


class SuccessResponse(BaseModel):
    success: bool = True