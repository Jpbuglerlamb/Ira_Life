# api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict

from auth.guard import get_user
from auth.tokens import create_token
from models.chat_request import ChatRequest
from models.chat_response import ChatResponse
from models.user import LoginRequest
from api.schemas import ModeRequest
from brain.director import process_input
from memory.long_term import UserService
from memory.short_term import EphemeralService

router = APIRouter()

class Mode(BaseModel):
    name: str
    description: str
    temperature: float = 0.5
    max_tokens: int = 400

AVAILABLE_MODES: Dict[str, Mode] = {
    "Secretary": Mode(name="Secretary", description="Office assistant, reminders, tasks", temperature=0.5, max_tokens=400),
    "Build": Mode(name="Build", description="Coding teacher, AI & electronics mentor", temperature=0.7, max_tokens=800),
    "VIP": Mode(name="VIP", description="Philosophical, conversational, creative mode", temperature=0.8, max_tokens=400),
}

user_modes: Dict[int, str] = {}

def get_user_mode(user_id: int) -> Mode:
    mode_name = user_modes.get(user_id, "Secretary")
    mode = AVAILABLE_MODES.get(mode_name) or AVAILABLE_MODES["Secretary"]
    user_modes[user_id] = mode.name
    return mode

@router.post("/login")
def login(req: LoginRequest, stay_logged_in: bool = False):
    user = UserService.get_user(req.username)
    if not user or not UserService.verify_user(req.username, req.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_modes.setdefault(user["id"], "Secretary")
    token = create_token(req.username, long_lived=stay_logged_in)

    return {"access_token": token, "token_type": "bearer", "stay_logged_in": stay_logged_in}

@router.post("/signup")
def signup(req: LoginRequest, stay_logged_in: bool = False):
    if not req.password:
        raise HTTPException(status_code=400, detail="Password required")

    existing = UserService.get_user(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = UserService.create_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")

    user_modes[user["id"]] = "Secretary"
    token = create_token(req.username, long_lived=stay_logged_in)

    return {
        "access_token": token,
        "token_type": "bearer",
        "stay_logged_in": stay_logged_in,
        "is_new_user": True
    }

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, username: str = Depends(get_user)):
    user = UserService.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user["id"]

    mode = get_user_mode(user_id)
    ai_text = process_input(user_id, mode.model_dump(), req.message)
    return ChatResponse(response=ai_text)

@router.post("/mode")
def change_mode(req: ModeRequest, username: str = Depends(get_user)):
    user = UserService.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user["id"]

    if req.mode not in AVAILABLE_MODES:
        raise HTTPException(status_code=400, detail=f"Mode '{req.mode}' not found. Available: {list(AVAILABLE_MODES.keys())}")

    user_modes[user_id] = req.mode
    EphemeralService.forget(user_id)
    return {"status": "ok", "mode": req.mode}
