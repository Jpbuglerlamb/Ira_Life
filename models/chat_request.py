# models/chat_request.py
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str