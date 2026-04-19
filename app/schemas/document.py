from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: float
    chunks_count: int
    created_at: datetime

    class Config:
        from_attributes = True