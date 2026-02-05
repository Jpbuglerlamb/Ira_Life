# models/chat_response.py
from pydantic import BaseModel

class ChatResponse(BaseModel):
    response: str