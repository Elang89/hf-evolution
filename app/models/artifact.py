from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Optional, Set

from app.models.artifact_commit import ArtifactCommit
from app.models.artifact_file import ArtifactFile
from app.models.author import Author
from app.models.issue import Issue


class Artifact(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    artifact_name: str
    artifact_type: int
    authors: Optional[List[Author]]
    commits: Optional[List[ArtifactCommit]]
    files: Optional[Set[ArtifactFile]]
    issues: Optional[List[Issue]]