from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Author(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    author_name: str
    author_email: str

    def __hash__(self):                                                         
        return hash(self.author_name)              
                                                                                
    def __eq__(self, other):                                                    
        return self.__hash__() == other.__hash__()  