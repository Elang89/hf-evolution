from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class GithubRepository(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    repository_name: str
    repository_type: int