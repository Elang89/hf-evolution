from pydantic import BaseModel, Field
from uuid import UUID, uuid4



class HfRepository(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    repository_name: str
    repository_type: int