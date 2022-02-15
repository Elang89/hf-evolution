import argparse
from pprint import pprint
import random
import sys
from typing import Dict, List, Tuple
from uuid import uuid4
import huggingface_hub

from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import register_uuid
from loguru import logger
from datasets import list_datasets
from multiprocessing import Queue


from app.resources.constants import (
    CMD_MINE_DATASETS,
    CMD_MINE_MODELS,
    COMMAND_LINE_OPTIONS, 
    COMMAND_LINE_DESCRIPTION,
    CMD_MINE_MODELS, 
    CMD_MINE_PRODUCTS,
    CONSUMER_KILL_SIG
)
from app.services.extractor import Extractor
from app.models.types import ArtifactType
from app.services.general_repository import GeneralRepository
from app.services.writer import Writer
from app.utils.consumer import Consumer
from app.utils.producer import Producer

class CommandLine(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description = COMMAND_LINE_DESCRIPTION,
            usage = COMMAND_LINE_OPTIONS
        )

        parser.add_argument("command", help="Subcommand to run")
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print("Unrecognized command")
            parser.print_help()
            exit(1)

        getattr(self, args.command)()


    def mine_datasets(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_DATASETS
        )

        try:
            register_uuid() 
            queue = Queue(maxsize=2000)
            pool = ThreadedConnectionPool(0, 500, user="root", password="password", host="localhost", dbname="hf")
            
            dataset_list = list_datasets(with_details=False, with_community_datasets=True)
            random.shuffle(dataset_list)
            dataset_list = [
                {"artifact_name": dataset, "artifact_url": f"https://huggingface.co/datasets/{dataset}"}
                for dataset in dataset_list
            ]


            dataset_list = [dataset_list[x:x + 150] for x in range(0, len(dataset_list), 150)]
            processes = self._initiate_threads(dataset_list, pool, ArtifactType.DATASET, queue)

            self._start_parallelization(processes, queue)


        except ValueError as error:
            logger.errors(error)
            exit(1)


    def mine_models(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_MODELS
        )

        try:
            register_uuid() 
            queue = Queue(maxsize=2000)
            pool = ThreadedConnectionPool(0, 500, user="root", password="password", host="localhost", dbname="hf")

            model_list = huggingface_hub.list_models(full=False)
            random.shuffle(model_list)
            model_list = [model.modelId for model in model_list]
            model_list = [{"artifact_name": model, "artifact_url": f"https://huggingface.co/{model}"} 
                for model in model_list]
            
            model_list = [model_list[x:x + 100] for x in range(0, len(model_list), 100)]

            processes = self._initiate_threads(model_list, pool, ArtifactType.MODEL, queue)
            self._start_parallelization(processes, queue)

        except ValueError as error:
            logger.error(str(error))
            exit(1)

    def mine_products(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_PRODUCTS
        )

        try:
            register_uuid() 
            queue = Queue
            pool = ThreadedConnectionPool(0, 500, user="root", password="password", host="localhost", dbname="hf")

            product_list = []
            

            processes = self._initiate_threads(product_list, pool, ArtifactType.MODEL)
            self._start_parallelization(processes, queue)



        except ValueError as error:
            logger.error(str(error))
            exit(1)

    def _initiate_threads(self, 
        artifact_list: List[Dict[str, str]],
        pool: ThreadedConnectionPool,
        artifact_type: ArtifactType, queue: Queue) -> Tuple[List, List]:

        producers = []
        consumers = []

        for artifact_group in range(len(artifact_list)):
            extractor = Extractor()
            conn = pool.getconn()
            repository = GeneralRepository(conn)
            writer = Writer(repository)

            producer = Producer(
                queue, 
                artifact_list[artifact_group], 
                extractor, 
                artifact_type
            )
            
            consumer = Consumer(queue, writer)
            
            consumers.append(consumer)
            producers.append(producer)

           


        
        return (producers, consumers)

    def _start_parallelization(self, processes: Tuple[List, List], queue: Queue):
        producers, consumers = processes

        for producer in producers:
            producer.start()

        for consumer in consumers: 
            consumer.start()


        while producers:
            for producer in producers:
                if not producer.is_alive():
                    if producer.finished_jobs < len(producer.artifacts):

                        logger.info(f"Producer-{producer.pid} down, restarting, jobs: {producer.finished_jobs}")

                        pprint(producer.artifacts)

                        new_producer = Producer(
                            producer.queue, 
                            producer.artifacts, 
                            producer.extractor, 
                            producer.artifact_type
                        )
                        
                        producer.join() 
                        producers.remove(producer)
                        new_producer.start()
                        producers.append(new_producer)
                        break
                        

                    logger.info(f"Producer-{producer.pid} finished, joining")

                    producers.remove(producer)
                    break
        
        queue.put(CONSUMER_KILL_SIG)

        for consumer in consumers:
            consumer.join()



