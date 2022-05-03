from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from app.models.issue_comment import IssueComment

class Issue(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    repository_id: UUID
    issue_title: str
    issue_description: str
    issue_timestamp: str
    issue_comment_num: int
    issue_assignees: int
    issue_closing_date: Optional[str]
    issue_number: str
    issue_comments: Optional[List[IssueComment]]