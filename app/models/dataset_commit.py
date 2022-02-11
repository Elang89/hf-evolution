from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class DatasetCommit(BaseModel):
    id: UUID
    author_id: UUID
    dataset_id: UUID
    commit_hash: str
    commit_message: str
    commit_timestamp: datetime
    insertions: int
    deletions: int
    total_lines_modified: int
    total_files_modified: int
    created_at: datetime
    updated_at: datetime