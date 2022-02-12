from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class Issue(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    artifact_id: UUID
    issue_title: str
    issue_description: str
    issue_timestamp: str