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
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(tb)
            self._cconn.send((e, tb))

    def consumer_workflow(self):
        while True:

            event_list = self.queue.get()

            if event_list == CONSUMER_KILL_SIG: 
                self.queue.put(event_list)
                logger.info(f"Consumer-{self.pid} exiting")
                break

            if event_list:
                logger.info(f"Consumer-{self.pid} db write")

                self.writer.insert_data(event_list)

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception
