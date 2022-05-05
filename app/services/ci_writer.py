
from typing import List
from app.models.ci_run import CiRun
from app.services.general_repository import GeneralRepository


class CiWriter(object):

    def __init__(self, repository: GeneralRepository):
        self.repository = repository
    
    def insert_data(self, ci_run: CiRun) -> None:
        runs = [ci_run.dict()]
        self.repository.insert("workflow_runs", runs)
        

