from typing import List, Set
from git import Commit
from pydriller import Repository, ModifiedFile
from faker import Faker
from pprint import pprint

from app.models.artifact import Artifact
from app.models.author import Author
from app.models.artifact_commit import ArtifactCommit
from app.models.artifact_file import ArtifactFile
from app.models.artifact_file_change import ArtifactFileChange
from app.models.types import ArtifactType

class Extractor(object):

    def retrieve_data(self, url: str, artifact_name: str, artifact_type: ArtifactType) -> Artifact:
        repo = Repository(url)
        format = "%Y-%m-%d %H:%M:%S.%f"

        authors = []
        seen_authors = set()
        files = []
        commits = []

        artifact = Artifact(artifact_name=artifact_name, artifact_type=artifact_type.value)

        for commit in repo.traverse_commits():
            dmm_unit_size = commit.dmm_unit_size if commit.dmm_unit_size else 0.0
            dmm_unit_complexity = commit.dmm_unit_complexity if commit.dmm_unit_complexity else 0.0
            dmm_unit_interfacing = commit.dmm_unit_interfacing if commit.dmm_unit_interfacing else 0.0


            author = self._create_author(seen_authors, commit, authors)
            artifact_commit = ArtifactCommit(
                artifact_id=str(artifact.id),
                author_id=str(author.id), 
                commit_hash=commit.hash,
                commit_message=commit.msg,
                author_timestamp=commit.author_date.strftime(format),
                commit_timestamp=commit.committer_date.strftime(format),
                insertions=commit.insertions,
                deletions=commit.deletions,
                total_lines_modified=commit.lines,
                total_files_modified=commit.files,
                dmm_unit_size=dmm_unit_size,
                dmm_unit_complexity=dmm_unit_complexity,
                dmm_unit_interfacing=dmm_unit_interfacing
            )
            
            files = [ArtifactFile(artifact_id=artifact.id, 
                artifact_commit_id=artifact_commit.id, 
                artifact_file_name=file.filename) 
                for file in commit.modified_files]
            
            
            file_changes = self._get_file_changes(artifact_commit, files, commit.modified_files)

            artifact_commit.file_changes = file_changes
            commits.append(artifact_commit)

        artifact.authors = authors
        artifact.files = files
        artifact.commits = commits

        return artifact

    def _get_file_changes(self, artifact_commit: ArtifactCommit, 
        files: List[ArtifactFile], commit_files: List[ModifiedFile]) -> List[ArtifactFileChange]:
        changes = []


        for file in files:
            commit_file = list(filter(lambda x: file.artifact_file_name == x.filename, commit_files))[0]
            cyclomatic_complexity = commit_file.complexity if commit_file.complexity else 0.0
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
        fake = Faker()
        if commit.author.name not in set: 
            set.add(commit.author.name)
            author = Author(
                author_name=commit.author.name, 
                author_fake_name=fake.name(), 
                author_email=commit.author.email)
            author_list.append(author)
            return author 
        
        author = list(filter(lambda x: x.author_name == commit.author.name, author_list))[0]
        return author


    



            

