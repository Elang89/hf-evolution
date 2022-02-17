from typing import List, Optional, Union
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class FileChange(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    change_type: str
    diff: str
    source_code: Optional[str]
    source_code_before: Optional[str]
    added_lines: int
    deleted_lines: int
    methods: Optional[List[str]]
    methods_before: Optional[List[str]]
    changed_methods: Optional[List[str]]
    nloc: int
    cyclomatic_complexity: float
    token_count: int
