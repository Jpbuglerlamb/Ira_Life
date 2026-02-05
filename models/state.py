# models/state.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageEntry(BaseModel):
    role: str          # "User", "AI", "System"
    content: str
    timestamp: datetime

class UserState(BaseModel):
    user_id: int
    username: str
    current_mode: str = "Secretary"
    last_active: datetime = datetime.utcnow()
    ephemeral_history: List[MessageEntry] = []
    waiting_for: Optional[str] = None  # e.g., "reminder_time" or "task_description"