
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from app.models.author import Author
from app.models.hf_repository import HfRepository

from app.models.hf_commit import HfCommit
from app.models.file_change import FileChange

class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    author_id: UUID
    commit_id: UUID
    file_change_id: UUID 
    repository_id: UUID
    author: Author
    repository: HfRepository
    file_change: FileChange
    commit: HfCommit

