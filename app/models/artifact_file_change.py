from typing import Optional, Union
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class ArtifactFileChange(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    artifact_file_id: UUID
    artifact_commit_id: UUID
    diff: str
    added_lines: int
    deleted_lines: int
    lines_of_code: int
    cyclomatic_complexity: float
