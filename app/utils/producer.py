import random
import time
import traceback

from multiprocessing import Pipe, Process, Queue
from typing import List, Dict
from git import GitCommandError
from loguru import logger

from app.services.extractor import Extractor
from app.services.writer import Writer

class Producer(Process): 

    def __init__(
            self, 
            queue: Queue, 
            extractor: Extractor,
            repositories: List[Dict[str, str]]
        ):
        
        super(Producer, self).__init__()
        self.queue = queue
        self.repositories = repositories
        self.extractor = extractor
    
    def run(self):
        self.run_producer_workflow()
        

    def run_producer_workflow(self) -> None:
        try:
            for event_list in self.extractor.retrieve_data(self.repositories):
                logger.info(f"Producer-{self.pid} created event list")
                self.queue.put(event_list)

        except GitCommandError as e:
            tb = traceback.format_exc()
            logger.error(tb)

