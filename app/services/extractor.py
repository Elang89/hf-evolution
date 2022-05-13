
from email.generator import Generator
from pprint import pprint
import time
from typing import List, Set, Dict
from git import Commit, GitCommandError
from loguru import logger
from pydriller import Repository, ModifiedFile
from app.models.event import Event

from app.models.hf_repository import HfRepository
from app.models.author import Author
from app.models.hf_commit import HfCommit
from app.models.file_change import FileChange

class Extractor(object):
    
    def __init__(self):
        self.format = "%Y-%m-%d %H:%M:%S.%f"

    def retrieve_data(self, repositories: List[Dict[str, str]]) -> List[Event]:
        repository_dict = {repository.get("repository_name").split("/")[-1]: 
            {"repo_name": repository.get("repository_name"), "repository_url": repository.get("repository_url"), "repository_type": repository.get("repository_type")} 
        for repository in repositories}

        repo = Repository([repository[1].get("repository_url") for repository in repository_dict.items()], num_workers=20)
        
        for commit in repo.traverse_commits():
            repository_type = repository_dict.get(commit.project_name).get("repository_type")
            repo_name = repository_dict.get(commit.project_name).get("repo_name")

            events = self._create_events(repo_name, repository_type, commit, commit.modified_files)
            yield events
            time.sleep(5)

    def _create_author(self, repo_commit: Commit) -> Author:
        return Author(author_name=repo_commit.author.name, author_email=repo_commit.author.email)

    def _create_commit(self, repo_commit: Commit) -> HfCommit:
        dmm_unit_size = round(repo_commit.dmm_unit_size, 3) if repo_commit.dmm_unit_size else -1.0
        dmm_unit_complexity = round(repo_commit.dmm_unit_complexity, 3) if repo_commit.dmm_unit_complexity else -1.0
        dmm_unit_interfacing = round(repo_commit.dmm_unit_interfacing, 3) if repo_commit.dmm_unit_interfacing else -1.0

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

    def _create_events(self, 
        repository_name: str, 
        repository_type: int, 
        repo_commit: Commit, file_changes: List[ModifiedFile]
    ):
        events = []

        for file_change in file_changes:
            hf_repository = HfRepository(repository_name=repository_name, repository_type=repository_type)
            author = self._create_author(repo_commit)
            commit = self._create_commit(repo_commit)
            new_path = file_change.new_path if file_change.new_path else None
            old_path = file_change.old_path if file_change.old_path else None
            cyclomatic_complexity = file_change.complexity if file_change.complexity else 0.0
            nloc = file_change.nloc if file_change.nloc else 0
            token_count = file_change.token_count if file_change.token_count else 0

            new_file_change = FileChange(
                filename=file_change.filename,
                new_path=new_path,
                old_path=old_path,
                added_lines=file_change.added_lines,
                deleted_lines=file_change.deleted_lines,
                change_type=file_change.change_type.value, 
                diff=file_change.diff,
                nloc=nloc,
                cyclomatic_complexity=cyclomatic_complexity,
                token_count=token_count
            )

            event = Event(
                author_id=author.id, 
                commit_id=commit.id, 
                file_change_id=new_file_change.id,
                repository_id=hf_repository.id,
                file_change=new_file_change,
                author=author,
                commit=commit,
                repository=hf_repository
            )

            events.append(event)

        return events