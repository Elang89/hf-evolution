import traceback

from loguru import logger
from multiprocessing import Pipe, Process, Queue
from app.resources.constants import CONSUMER_KILL_SIG

from app.services.writer import Writer



class Consumer(Process): 

    def __init__(self, queue: Queue, writer: Writer):
        super(Consumer, self).__init__()
        self._pconn, self._cconn = Pipe()
        self._exception = None
        self.queue = queue
        self.writer = writer
    
    def run(self):
        try:
            self.consumer_workflow()
        except Exception as e:
            logger.error(e)

    def consumer_workflow(self):
        while True:
            artifact = self.queue.get()

            if artifact == CONSUMER_KILL_SIG: 
                self.queue.put(artifact)
                logger.info(f"Consumer-{self.pid} exiting")
                break

            if artifact:
                logger.info(f"Consumer-{self.pid} db write")

                self.writer.insert_data(artifact)

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception
