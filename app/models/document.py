from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id          = Column(Integer, primary_key=True, index=True)
    filename    = Column(String, nullable=False)
    file_size   = Column(Float)                    # بالـ MB
    chunks_count = Column(Integer, default=0)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner       = relationship("User", back_populates="documents")