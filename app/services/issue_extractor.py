
from pprint import pprint
from typing import List, Dict
from uuid import UUID, uuid4

from github import Github, Issue
from app.models.github_repository import GithubRepository
from app.models.issue import GithubIssue, GithubIssueComment
from app.services.general_repository import GeneralRepository


class IssueExtractor(object): 
    
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

    def retrieve_data(self) -> GithubIssue:
        issues = self.repo.get_issues()

        for issue in issues:
            extracted_issue = self.create_issue(issue)
            yield extracted_issue


    def create_issue(self, issue: Issue) -> GithubIssue:
        active_lock_reason = issue.active_lock_reason if issue.active_lock_reason else None
        issue_closing_date = issue.closed_at.strftime(self.format) if issue.closed_at else None

        new_issue = GithubIssue(
            github_repository_id=self.repository_id,
            issue_title=issue.title,
            issue_description=issue.body,
            issue_timestamp=issue.created_at.strftime(self.format),
            issue_state=issue.state,
            issue_locked=issue.locked,
            issue_lock_reason=active_lock_reason,
            issue_comment_num=0,
            issue_assignees=len(issue.assignees),
            issue_closing_date=issue_closing_date,
            issue_number=issue.number,
        )

        comments = [
            GithubIssueComment(
                issue_comment_body=comment.body,
                issue_id=new_issue.id,
                issue_comment_length=len(comment.body),
                issue_comment_timestamp=comment.created_at.strftime(self.format)
            )
        for comment in issue.get_comments()]

        new_issue.issue_comments = comments
        new_issue.issue_comment_num = len(comments)

        return new_issue