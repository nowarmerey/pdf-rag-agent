from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[int] = None
    language: Optional[str] = "de"

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: int