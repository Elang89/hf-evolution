import time
import traceback

from multiprocessing import Pipe, Process, Queue
from typing import List, Dict
from git import GitCommandError
from loguru import logger

from app.models.types import ArtifactType
from app.services.extractor import Extractor

class Producer(Process): 

    def __init__(
            self, 
            queue: Queue, 
            artifacts: List[Dict[str, str]],
            extractor: Extractor,
            artifact_type: ArtifactType, 
        ):
        
        super(Producer, self).__init__()
        self.queue = queue
        self.artifacts = artifacts
        self.extractor = extractor
        self.artifact_type = artifact_type
        self.finished_jobs = 0
    
    def run(self):
        try:
            self.run_producer_workflow()
        except Exception as e: 
            self.finished_jobs += 1
            logger.error(e)

    def run_producer_workflow(self) -> None:
        for artifact in self.artifacts:
            artifact_name  = artifact.get("artifact_name")
            artifact_url = artifact.get("artifact_url")

            try:
                artifact = self.extractor.retrieve_data(artifact_url, artifact_name, self.artifact_type)
                self.queue.put(artifact)

                self.finished_jobs += 1
                
                logger.info(f"Producer-{self.pid} created artifact, {self.finished_jobs}/{len(self.artifacts)}")
                # timeout = 10
                # time.sleep(10)

                # logger.info(f"Producer-{self.pid} timeout: {timeout}")

            except GitCommandError as error:
                logger.error(error)
                self.artifacts.remove(artifact)
