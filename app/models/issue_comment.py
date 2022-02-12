from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field

class IssueComment(BaseModel):
    id: str = Field(default_factory=uuid4)
    issue_id: str
    issue_comment_body: str
    issue_comment_timestamp: str