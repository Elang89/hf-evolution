from multiprocessing import Queue
from app.models.artifact import Artifact
from app.services.general_repository import GeneralRepository


class Writer(object):

    def __init__(self, repository: GeneralRepository):
        self.repository = repository

    def insert_data(self, artifact: Artifact):
        artifact_dict = dict(artifact)

        authors = [author.dict() for author in artifact.authors]
        commits = [commit.dict() for commit in artifact.commits]
        files = [file.dict() for file in artifact.files] 
        
        changes = [commit.pop("file_changes") for commit in commits]

        artifact_dict.pop("authors")
        artifact_dict.pop("commits")
        artifact_dict.pop("files")
        artifact_dict.pop("issues")

        self.repository.insert("artifacts", [artifact_dict])
        self.repository.insert("authors", authors)
        self.repository.insert("artifact_commits", commits)
        self.repository.insert("artifact_files", files)
