from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class ArtifactFile(BaseModel):
    id: UUID  = Field(default_factory=uuid4)
    artifact_id: UUID
    artifact_commit_id: UUID
    artifact_file_name: str

    def __hash__(self):                                                         
        return hash(self.artifact_file_name)              
                                                                                
    def __eq__(self, other):                                                    
        return self.__hash__() == other.__hash__()  
