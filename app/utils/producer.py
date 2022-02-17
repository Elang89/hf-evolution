from csv import excel_tab
import random
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
            repositories: List[Dict[str, str]],
            extractor: Extractor
        ):
        
        super(Producer, self).__init__()
        self._pconn, self._cconn = Pipe()
        self._exception = None
        self.queue = queue
        self.repositories = repositories
        self.extractor = extractor
    
    def run(self):
        try:
            self.run_producer_workflow()
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(tb)
            self._cconn.send((e, tb))
        

    def run_producer_workflow(self) -> None:
        for repository in self.repositories:

            event_list = self.extractor.retrieve_data(repository)
            self.queue.put(event_list)
            
            logger.info(f"Producer-{self.pid} created artifact, {len(self.artifacts)} left")
            self.artifacts.remove(repository)

