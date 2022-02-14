import random
import time

from multiprocessing import Queue
from typing import Dict, List
from uuid import UUID
from loguru import logger

from app.models.types import ArtifactType
from app.services.extractor import Extractor

def run_producer_workflow(
    queue: Queue, 
    artifacts: List[Dict[str,str]], 
    extractor: Extractor, 
    artifact_type: ArtifactType,
    pid: UUID) -> None:

    for artifact in artifacts:
        artifact_name  = artifact.get("artifact_name")
        artifact_url = artifact.get("artifact_url")

        artifact = extractor.retrieve_data(artifact_url, artifact_name, artifact_type)
        queue.put(artifact)

        logger.info(f"Producer-{pid} created artifact and inserted into queue")
        # timeout = random.randint(1, 10)
        # logger.info(f"Timing out Producer-{pid} for {timeout} seconds")

        # time.sleep(timeout)
