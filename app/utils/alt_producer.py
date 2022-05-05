from multiprocessing import Process, Queue
from typing import Dict, Union
from loguru import logger
from app.services.ci_extractor import CiExtractor

from app.services.issue_extractor import IssueExtractor


class AltProducer(Process):

    def __init__(
            self, 
            queue: Queue, 
            extractor: Union[IssueExtractor, CiExtractor],
            repository: Dict[str, str]
        ): 

        super(AltProducer, self).__init__()
        self.queue = queue
        self.repository = repository
        self.extractor = extractor

    def run(self) -> None:
        self.run_producer_workflow()

    
    def run_producer_workflow(self) -> None:
        for item in self.extractor.retrieve_data():
            logger.info(f"AltProducer-{self.pid} created item")
            self.queue.put(item)