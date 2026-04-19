from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String, default="New Chat")
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner      = relationship("User", back_populates="chat_sessions")
    messages   = relationship("ChatMessage", back_populates="session",
                               cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, index=True)
    role       = Column(String, nullable=False)   # "user" or "assistant"
    content    = Column(Text, nullable=False)
    sources    = Column(String, nullable=True)     # JSON string of sources
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session    = relationship("ChatSession", back_populates="messages")