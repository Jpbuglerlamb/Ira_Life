#api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List

from auth.guard import get_user
from auth.tokens import create_token
from models.chat_request import ChatRequest
from models.chat_response import ChatResponse
from models.user import LoginRequest
from api.schemas import ModeRequest
from brain.director import process_input
from memory.long_term import MemoryService, UserService
from memory.short_term import EphemeralService
from api.profile.schemas import UpdateProfileRequest, ProfileResponse

router = APIRouter()

# -----------------------------
# Mode Model
# -----------------------------
class Mode(BaseModel):
    name: str
    description: str
    temperature: float = 0.5
    max_tokens: int = 400

# Define available modes
AVAILABLE_MODES: Dict[str, Mode] = {
    "Secretary": Mode(
        name="Secretary",
        description="Office assistant, reminders, tasks",
        temperature=0.5,
        max_tokens=400
    ),
    "Build": Mode(
        name="Build",
        description="Coding teacher, AI & electronics mentor",
        temperature=0.7,
        max_tokens=800
    ),
    "VIP": Mode(
        name="VIP",
        description="Philosophical, conversational, creative mode",
        temperature=0.8,
        max_tokens=400
    )
}

# Tracks current mode per user
user_modes: Dict[int, str] = {}  # {user_id: mode_name}


# -----------------------------
# Helpers
# -----------------------------
def get_user_mode(user_id: int) -> Mode:
    """Return the Mode object for a user, default to Secretary."""
    mode_name = user_modes.get(user_id, "Secretary")
    mode = AVAILABLE_MODES.get(mode_name)
    if not mode:
        # fallback to Secretary if mode missing
        mode = AVAILABLE_MODES["Secretary"]
        user_modes[user_id] = "Secretary"
    return mode


# -----------------------------
# Auth Endpoints (Fixed)
# -----------------------------
# login
@router.post("/login")
def login(req: LoginRequest, stay_logged_in: bool = False):
    user = UserService.get_user(req.username)
    if not user or not UserService.verify_user(req.username, req.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # default mode fallback
    mode_name = user_modes.get(user["id"], "Secretary")
    user_modes[user["id"]] = mode_name

    token = create_token(req.username, long_lived=stay_logged_in)

    # Track welcome screen
    if MemoryService.recall(user["id"], "Profile", "welcome_seen") is None:
        MemoryService.remember(user["id"], "Profile", "welcome_seen", False)

    return {
        "access_token": token,
        "token_type": "bearer",
        "stay_logged_in": stay_logged_in
    }

# signup
@router.post("/signup")
def signup(req: LoginRequest, stay_logged_in: bool = False):
    existing = UserService.get_user(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = UserService.create_user(req.username, req.password)

    # Default memories
    MemoryService.remember(user["id"], "Profile", "welcome_seen", False)

    token = create_token(req.username, long_lived=stay_logged_in)
    return {
        "access_token": token,
        "token_type": "bearer",
        "stay_logged_in": stay_logged_in,
        "is_new_user": True
    }


# -----------------------------
# Profile / Memory Endpoints (Fixed)
# -----------------------------
@router.post("/profile/update")
def update_profile(req: UpdateProfileRequest, username: str = Depends(get_user)):
    user = UserService.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user.id

    MemoryService.remember(user_id, "Profile", "fullName", req.fullName)
    MemoryService.remember(user_id, "Profile", "email", req.email)
    MemoryService.remember(user_id, "Profile", "aiPersonality", req.aiPersonality)
    return {"success": True}


@router.get("/profile", response_model=ProfileResponse)
def get_profile(username: str = Depends(get_user)):
    user = UserService.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user.id

    fullName = MemoryService.recall(user_id, "Profile", "fullName") or ""
    email = MemoryService.recall(user_id, "Profile", "email") or ""
    aiPersonality = MemoryService.recall(user_id, "Profile", "aiPersonality") or ""
    return ProfileResponse(fullName=fullName, email=email, aiPersonality=aiPersonality)


# -----------------------------
# Chat Endpoint (Fixed)
# -----------------------------
@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, username: str = Depends(get_user)):
    user = UserService.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user["id"]  # <-- fix here

    mode = get_user_mode(user_id)
    ai_text = process_input(user_id, mode, req.message)
    return {"response": ai_text}


# -----------------------------
# Mode Management (Fixed)
# -----------------------------
@router.post("/mode")
def change_mode(req: ModeRequest, username: str = Depends(get_user)):
    user = UserService.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user["id"]  # <-- fixed

    if req.mode not in AVAILABLE_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"Mode '{req.mode}' not found. Available modes: {list(AVAILABLE_MODES.keys())}"
        )

    user_modes[user_id] = req.mode
    EphemeralService.forget(user_id)  # clear ephemeral memory when switching modes
    return {"status": "ok", "mode": req.mode}