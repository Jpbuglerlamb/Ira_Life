#api/profile/routes.py
from fastapi import APIRouter, HTTPException, Depends
from memory.long_term import MemoryService, UserService
from api.profile.schemas import ProfileResponse, UpdateProfileRequest
from auth.guard import get_user

router = APIRouter(prefix="/profile", tags=["Profile"])

# GET profile
@router.get("/", response_model=ProfileResponse)
def get_profile(username: str = Depends(get_user)):
    user_id = UserService.get_user_id(username)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    fullName = MemoryService.recall(user_id, "Profile", "fullName") or ""
    email = MemoryService.recall(user_id, "Profile", "email") or ""
    
    return ProfileResponse(
        fullName=fullName,
        email=email,
        notificationsEnabled=False  # default for now
    )

# POST update profile
@router.post("/update", response_model=ProfileResponse)
def update_profile(req: UpdateProfileRequest, username: str = Depends(get_user)):
    user_id = UserService.get_or_create_user(username)
    MemoryService.remember(user_id, "Profile", "fullName", req.fullName)
    MemoryService.remember(user_id, "Profile", "email", req.email)
    
    return ProfileResponse(
        fullName=req.fullName,
        email=req.email,
        notificationsEnabled=False  # default, frontend can trigger notifications separately
    )
