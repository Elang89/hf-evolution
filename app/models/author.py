from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class Author(BaseModel):
    id: UUID
    author_name: str
    author_fake_name: str
    author_email: str
    created_at: datetime
    updated_at: datetime