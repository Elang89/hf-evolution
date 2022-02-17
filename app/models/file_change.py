from optparse import Option
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class FileChange(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    change_type: int
    diff: str
    added_lines: int
    deleted_lines: int
    nloc: int
    cyclomatic_complexity: float
    token_count: int
