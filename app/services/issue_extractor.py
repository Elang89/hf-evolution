
from typing import List, Dict
from app.models.issue import Issue


class IssueExtractor(object): 
    
    def __init__(self):
        self.format = "%Y-%m-%d %H:%M:%S.%f"

    def retrieve_data(self, repositories: List[Dict[str, str]]) -> List[Issue]: 
        pass