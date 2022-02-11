from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class Model(BaseModel):
    id: UUID
    model_name: str
    created_at: datetime
    updated_at: datetime