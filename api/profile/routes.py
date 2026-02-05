# api/profile/routes.py
from fastapi import APIRouter, HTTPException, Depends
from memory.long_term import MemoryService, UserService
from api.profile.schemas import ProfileResponse, UpdateProfileRequest
from auth.guard import get_user

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/", response_model=ProfileResponse)
def get_profile(username: str = Depends(get_user)):
    user_id = UserService.get_user_id(username)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    fullName = MemoryService.recall(user_id, "Profile", "fullName") or ""
    email = MemoryService.recall(user_id, "Profile", "email") or ""
    aiPersonality = MemoryService.recall(user_id, "Profile", "aiPersonality") or ""
    preferences = MemoryService.recall(user_id, "Profile", "preferences") or ""
    notificationsEnabled = MemoryService.recall(user_id, "Profile", "notificationsEnabled")
    notificationsEnabled = True if notificationsEnabled in (None, "", "True", True) else False

    return ProfileResponse(
        fullName=fullName,
        email=email,
        aiPersonality=aiPersonality,
        preferences=preferences,
        notificationsEnabled=notificationsEnabled
    )

@router.post("/update", response_model=ProfileResponse)
def update_profile(req: UpdateProfileRequest, username: str = Depends(get_user)):
    user = UserService.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user["id"]

    MemoryService.remember(user_id, "Profile", "fullName", req.fullName)
    MemoryService.remember(user_id, "Profile", "email", req.email)
    MemoryService.remember(user_id, "Profile", "aiPersonality", req.aiPersonality)
    MemoryService.remember(user_id, "Profile", "preferences", req.preferences)
    MemoryService.remember(user_id, "Profile", "notificationsEnabled", str(req.notificationsEnabled))

    return ProfileResponse(
        fullName=req.fullName,
        email=req.email,
        aiPersonality=req.aiPersonality,
        preferences=req.preferences,
        notificationsEnabled=req.notificationsEnabled
    )
