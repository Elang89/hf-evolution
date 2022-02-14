from multiprocessing import Queue
from uuid import UUID

from loguru import logger
from app.resources.constants import CONSUMER_KILL_SIG

from app.services.writer import Writer

def run_consumer_workflow(queue: Queue, writer: Writer, pid: UUID) -> None:
    while True:
        
        logger.info(f"Queue Size: {queue.qsize()}") 
        artifact = queue.get()

        if artifact == CONSUMER_KILL_SIG: 
            queue.put(artifact)
            logger.info(f"Consumer-{pid} exiting")
            break

        if artifact:
            logger.info(f"Consumer-{pid} retrieved artifact from queue and inserted into database")

            writer.insert_data(artifact)

    
