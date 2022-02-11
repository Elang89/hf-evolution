from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class Product(BaseModel):
    id: UUID
    product_name: str
    created_at: datetime
    updated_at: datetime