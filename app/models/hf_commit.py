from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class HfCommit(BaseModel):
    id: UUID = Field(default_factory=uuid4)
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

