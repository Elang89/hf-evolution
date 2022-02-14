import os

from typing import List, Set, Dict
from git import Commit
from pydriller import Repository, ModifiedFile
from pprint import pprint
from github import Github

from app.models.artifact import Artifact
from app.models.author import Author
from app.models.artifact_commit import ArtifactCommit
from app.models.artifact_file import ArtifactFile
from app.models.artifact_file_change import ArtifactFileChange
from app.models.issue import Issue
from app.models.issue_comment import IssueComment
from app.models.types import ArtifactType

class Extractor(object):

    def __init__(self):
        self.format = "%Y-%m-%d %H:%M:%S.%f"

    def retrieve_data(self, url: str, artifact_name: str, artifact_type: ArtifactType) -> Artifact:
        repo = Repository(url)

        authors = []
        seen_authors = set()
        files = []
        seen_files = {}
        commits = []

        artifact = Artifact(artifact_name=artifact_name, artifact_type=artifact_type.value)

        if artifact_type == ArtifactType.PRODUCT:
            self._extract_issues(artifact, artifact_name)

        for commit in repo.traverse_commits():
            dmm_unit_size = round(commit.dmm_unit_size, 3) if commit.dmm_unit_size else 0.0
            dmm_unit_complexity = round(commit.dmm_unit_complexity, 3) if commit.dmm_unit_complexity else 0.0
            dmm_unit_interfacing = round(commit.dmm_unit_interfacing, 3) if commit.dmm_unit_interfacing else 0.0


            author = self._create_author(seen_authors, commit, authors)
            artifact_commit = ArtifactCommit(
                artifact_id=str(artifact.id),
                author_id=str(author.id),
                author_name=author.author_name, 
                commit_hash=commit.hash,
                commit_message=commit.msg,
                author_timestamp=commit.author_date.strftime(self.format),
                commit_timestamp=commit.committer_date.strftime(self.format),
                insertions=commit.insertions,
                deletions=commit.deletions,
                total_lines_modified=commit.lines,
                total_files_modified=commit.files,
                dmm_unit_size=dmm_unit_size,
                dmm_unit_complexity=dmm_unit_complexity,
                dmm_unit_interfacing=dmm_unit_interfacing
            )

            files = self._create_file_list(seen_files, commit, artifact, artifact_commit)

            if files:
                file_changes = self._get_file_changes(artifact_commit, files, commit.modified_files)
                artifact_commit.file_changes = file_changes

            commits.append(artifact_commit)

        artifact.authors = authors
        artifact.files = list(seen_files.values())
        artifact.commits = commits

        return artifact

    def _get_file_changes(self, artifact_commit: ArtifactCommit, 
        files: List[ArtifactFile], commit_files: List[ModifiedFile]) -> List[ArtifactFileChange]:
        changes = []


        for file in files:
            commit_file = list(filter(lambda x: file.artifact_file_name == x.filename, commit_files))[0]
            cyclomatic_complexity = round(commit_file.complexity, 3) if commit_file.complexity else 0.0
            lines_of_code = commit_file.nloc if commit_file.nloc else 0

            file_change = ArtifactFileChange(artifact_file_id=file.id, 
                    artifact_commit_id=artifact_commit.id,
                    diff=commit_file.diff,
                    added_lines=commit_file.added_lines,
                    deleted_lines=commit_file.deleted_lines,
                    lines_of_code=lines_of_code,
                    cyclomatic_complexity=cyclomatic_complexity)
            changes.append(file_change)
        return changes
    
    def _create_author(self, set: Set, commit: Commit, author_list: List[Author]) -> Author:
        if commit.author.name not in set: 
            set.add(commit.author.name)
            author = Author(
                author_name=commit.author.name,  
                author_email=commit.author.email)
            author_list.append(author)
            return author 
        
        author = list(filter(lambda x: x.author_name == commit.author.name, author_list))[0]
        return author
    
    def _create_file_list(self, 
        seen_files: Dict[str, ArtifactFile], 
        commit: Commit, artifact: Artifact, 
        artifact_commit: ArtifactCommit) -> List[ArtifactFile]:

        modified_files = commit.modified_files
        files = []

        for modified_file in modified_files:
            if modified_file.filename in seen_files.keys():
                file = seen_files.get(modified_file.filename)
                files.append(file)
            else: 
                file = ArtifactFile(artifact_id=artifact.id, 
                artifact_commit_id=artifact_commit.id, 
                artifact_file_name=modified_file.filename)
                seen_files.update({modified_file.filename: file})
                files.append(file) 

            return files 
    
    def _extract_issues(self, artifact: Artifact, product: str) -> None:
        token = os.environ.get("GITHUB_ACCESS_TOKEN")
        g = Github(token)
        repo = g.get_repo(product)

        issues = []
        repo_issues = repo.get_issues()

        for repo_issue in repo_issues:
            issue_closing_date = repo_issue.closed_at.strftime() if repo_issue.closed_at else None

            issue = Issue(artifact_id=artifact.id, 
                issue_title=repo_issue.title,
                issue_timestamp=repo_issue.created_at.strftime(self.format),
                issue_closing_date=issue_closing_date,
                issue_description=repo_issue.body,
                issue_comment_num=repo_issue.comments,
                issue_assignees=len(repo_issue.assignees),
                issue_number=repo_issue.number
            )

            if repo_issue.get_comments():
                comments = [
                    IssueComment(issue_id=issue.id, 
                        issue_comment_body=comment.body, 
                        issue_comment_timestamp=comment.created_at.strftime(self.format)
                    ) for comment in repo_issue.get_comments()
                ]

                issue.issue_comments = comments
            issues.append(issue)

        artifact.issues = issues






                
        


    



            

