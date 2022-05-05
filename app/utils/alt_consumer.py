from typing import Union
from loguru import logger
from multiprocessing import Process, Queue
from app.resources.constants import CONSUMER_KILL_SIG

from app.services.ci_writer import CiWriter
from app.services.issue_writer import IssueWriter


class AltConsumer(Process):

    def __init__(self, queue: Queue, writer: Union[CiWriter, IssueWriter]):
        super(AltConsumer, self).__init__()
        self.queue = queue
        self.writer = writer

    def run(self):
        self.consumer_workflow()
    
    def consumer_workflow(self):
        while True:

            item = self.queue.get()

            if item == CONSUMER_KILL_SIG:
                self.queue.put(item)
                logger.info(f"AltConsumer-{self.pid} exiting")
                break

            if item: 
                logger.info(f"AltConsumer-{self.pid} db write")
                self.writer.insert_data(item)