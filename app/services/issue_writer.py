
from typing import List

from app.models.issue import GithubIssue
from app.services.general_repository import GeneralRepository


class IssueWriter(object):

    def __init__(self, repository: GeneralRepository):
        self.repository = repository
    
    def insert_data(self, issue: GithubIssue) -> None:
        issue_dict = issue.dict()
        comments = issue_dict.pop("issue_comments")


        self.repository.insert("issues", [issue_dict])

        if comments:
            self.repository.insert("issue_comments", comments)


