from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class Dataset(BaseModel):
    id: UUID
    dataset_name: str
    created_at: datetime
    updated_at: datetime

class DatasetDTO(BaseModel):
    dataset_name: str