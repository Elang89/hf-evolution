from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class GithubIssueComment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    issue_id: UUID
    issue_comment_body: str
    issue_comment_length: int
    issue_comment_timestamp: str