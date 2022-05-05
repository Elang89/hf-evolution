
from pprint import pprint
import time
from typing import List, Dict
from uuid import UUID, uuid4

from github import Github, WorkflowRun
from app.models.ci_run import CiRun
from app.models.github_repository import GithubRepository
from app.services.general_repository import GeneralRepository


class CiExtractor(object): 
    
    def __init__(self, access_token: str, repository: Dict[str, str], db_repo: GeneralRepository):
        self.format = "%Y-%m-%d %H:%M:%S.%f"
        g = Github(access_token)

        name = repository.get("repository_name")
        type = repository.get("repository_type")
        self.repo = g.get_repo(name)

        result = db_repo.get("github_repositories", name)

        if result: 
            self.repository_id = result[0]
        else: 
            repo = GithubRepository(repository_name=name, repository_type=type)
            data_points = [repo.dict()]

            self.repository_id = repo.id
            db_repo.insert("github_repositories", data_points)


    def retrieve_data(self) -> CiRun:
        runs = self.repo.get_workflow_runs()

        for run in runs:
            extracted_run = self.create_run(run)
            yield extracted_run
            time.sleep(2)


    def create_run(self, workflow_run: WorkflowRun) -> CiRun:
        timing = workflow_run.timing()
        duration = timing.run_duration_ms if hasattr(timing, "run_duration_ms") else None
        new_run = CiRun(
            github_repository_id=self.repository_id,
            run_number=workflow_run.run_number,
            run_timestamp=workflow_run.created_at.strftime(self.format),
            event=workflow_run.event,
            status=workflow_run.status,
            conclusion=workflow_run.conclusion,
            duration_ms=duration,
        )

        return new_run