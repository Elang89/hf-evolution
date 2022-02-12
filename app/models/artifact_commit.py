from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional, Union

from app.models.artifact_file_change import ArtifactFileChange

class ArtifactCommit(BaseModel):
    id: UUID =  Field(default_factory=uuid4)
    author_id: UUID
    artifact_id: UUID
    commit_hash: str
    commit_message: str
    author_timestamp: str
    commit_timestamp: str
    insertions: int
    deletions: int
    total_lines_modified: int
    total_files_modified: int
    dmm_unit_size: float
    dmm_unit_complexity: float
    dmm_unit_interfacing: float
    file_changes: Optional[List[ArtifactFileChange]]


