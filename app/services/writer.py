from typing import Any, Dict, List
from pprint import pprint

from app.models.artifact import Artifact
from app.models.artifact_commit import ArtifactCommit
from app.models.author import Author
from app.models.issue import Issue
from app.services.general_repository import GeneralRepository


class Writer(object):

    def __init__(self, repository: GeneralRepository):
        self.repository = repository

    def insert_data(self, artifact: Artifact):
        artifact_dict = dict(artifact)
        
        authors = artifact.authors
        authors = self._remove_duplicate_authors(authors)
        authors = [author.dict() for author in authors]

        commits = [commit.dict() for commit in artifact.commits]
        commits = self._fix_commit_authors(commits)
        files = [file.dict() for file in artifact.files] 
        changes = self._extract_file_changes(commits)

        artifact_dict.pop("authors")
        artifact_dict.pop("commits")
        artifact_dict.pop("files")
        issues = artifact_dict.pop("issues")

        self.repository.insert("artifacts", [artifact_dict])
        
        if authors: 
            self.repository.insert("authors", authors)
        
        if commits:
            self.repository.insert("artifact_commits", commits)

        if files: 
            changes = [change for sublist in changes for change in sublist]
            self.repository.insert("artifact_files", files)
            self.repository.insert("artifact_file_changes", changes)

        if issues:
            issues = [issue.dict() for issue in artifact.issues]
            issue_comments = self._extract_issue_comments(issues)
            issue_comments = [issue_comment for sublist in issue_comments for issue_comment in sublist]
            self.repository.insert("issues", issues)
            self.repository.insert("issue_comments", issue_comments)

    def _extract_file_changes(self, commits: List[ArtifactCommit]) -> List[Dict[str, Dict[str, Any]]]:
        changes = []

        for commit in commits:
            if commit.get("file_changes"):
                changes.append(commit.get("file_changes"))
            commit.pop("file_changes")

        return changes

    def _extract_issue_comments(self, issues: List[Issue]) -> List[Dict[str, Dict[str, Any]]]:
        issue_comments = []

        for issue in issues:
            if issue.get("issue_comments"):
                issue_comments.append(issue.get("issue_comments"))
            issue.pop("issue_comments")
        
        return issue_comments


    def _fix_commit_authors(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        
        for commit in commits:
            author_id = self.repository.get_author(commit.get("author_name"))

            if author_id  and author_id != commit.get("author_id"):
                commit.update({"author_id": author_id[0]})
            
            commit.pop("author_name")
        
        return commits

    def _remove_duplicate_authors(self, authors: List[Author]) -> List[Author]:
        new_authors = []

        for author in authors:
            author_exists = self.repository.get_author(author.author_name)

            if not author_exists:
                new_authors.append(author)
        
        return new_authors

