from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class CiRun(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    github_repository_id: UUID
    event: str
    run_timestamp: str 
    run_number: int 
    status: str
    duration_ms: Optional[int]
    conclusion: Optional[str]
