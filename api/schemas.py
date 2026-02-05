# api/schemas.py
from pydantic import BaseModel
from typing import List

class ModeRequest(BaseModel):
    mode: str

class ModesResponse(BaseModel):
    modes: List[str]
