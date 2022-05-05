from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from app.models.issue_comment import GithubIssueComment

class GithubIssue(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    github_repository_id: UUID
    issue_title: str
    issue_description: Optional[str]
    issue_timestamp: str
    issue_state: str
    issue_locked: bool
    issue_lock_reason: Optional[str]
    issue_comment_num: int
    issue_assignees: int
    issue_closing_date: Optional[str]
    issue_number: int
    issue_comments: Optional[List[GithubIssueComment]]