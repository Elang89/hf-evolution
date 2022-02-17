import os

from typing import List, Set, Dict
from git import Commit
from pydriller import Repository, ModifiedFile
from app.models.event import Event

from app.models.hf_repository import HfRepository
from app.models.author import Author
from app.models.hf_commit import HfCommit
from app.models.file_change import FileChange
from app.models.issue import Issue
from app.models.issue_comment import IssueComment
from app.models.types import ArtifactType
from app.services.general_repository import GeneralRepository

class Extractor(object):
    
    def __init__(self):
        self.format = "%Y-%m-%d %H:%M:%S.%f"

    def retrieve_data(self, repository: Dict[str, str]) -> List[Event]:
        repository_name = repository.get("repository_name")
        repository_type = repository.get("repository_type")
        repo = Repository(repository.get("repository_url"))

        hf_repository = HfRepository(repository_name=repository_name, repository_type=repository_type)
        events = []

        for repo_commit in repo.traverse_commits():
            author = Author(author_name=commit.author.name, author_email=commit.author_email)
            commit = self._create_commit(repo_commit)
            events += self._create_events(hf_repository, author, commit, repo_commit.modified_files)

        return events

    def _create_commit(self, repo_commit: Commit) -> HfCommit:
        dmm_unit_size = round(repo_commit.dmm_unit_size, 3) if repo_commit.dmm_unit_size else 0.0
        dmm_unit_complexity = round(repo_commit.dmm_unit_complexity, 3) if repo_commit.dmm_unit_complexity else 0.0
        dmm_unit_interfacing = round(repo_commit.dmm_unit_interfacing, 3) if repo_commit.dmm_unit_interfacing else 0.0

        return HfCommit(
            commit_hash=repo_commit.hash,
            commit_message=repo_commit.msg,
            author_timestamp=repo_commit.author_date.strftime(self.format),
            commit_timestamp=repo_commit.committer_date.strftime(self.format),
            insertions=repo_commit.insertions,
            deletions=repo_commit.deletions,
            total_lines_modified=repo_commit.lines,
            total_files_modified=repo_commit.files,
            dmm_unit_size=dmm_unit_size,
            dmm_unit_complexity=dmm_unit_complexity,
            dmm_unit_interfacing=dmm_unit_interfacing
        )

    def _create_events(self, repository: HfRepository, author: Author, commit: HfCommit, file_changes: List[ModifiedFile]):
        events = []

        for file_change in file_changes:
            cyclomatic_complexity = file_change.complexity if file_change.complexity else 0.0
            nloc = file_change.nloc if file_change.nloc else 0
            source_code = file_change.source_code if file_change.source_code else None
            source_code_before = file_change.source_code_before if file_change.source_code_before else None
            methods = file_change.methods if file_change.methods else None
            methods_before = file_change.methods_before if file_change.methods_before else None
            changed_methods = file_change.changed_methods if file_change.changed_methods else None 
            tokens = file_change.tokens if file_change.tokens else 0

            new_file_change = FileChange(
                added_lines=file_change.added_lines,
                deleted_lines=file_change.deleted_lines,
                change_type=file_change.change_type, 
                diff=file_change.diff,
                source_code=source_code,
                source_code_before=source_code_before,
                methods=methods,
                methods_before=methods_before,
                changed_methods=changed_methods,
                nloc=nloc,
                cyclomatic_complexity=cyclomatic_complexity,
                tokens=tokens
            )

            event = Event(
                author_id=author.id, 
                commit_id=commit.id, 
                file_change_id=new_file_change.id,
                repository_id=repository.id,
                file_change=new_file_change,
                author=author,
                commit=commit,
                repository=repository
            )

            events.append(event)

        return events