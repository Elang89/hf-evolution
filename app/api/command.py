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
    CMD_MINE_REPOSITORIES,
    COMMAND_LINE_OPTIONS, 
    COMMAND_LINE_DESCRIPTION,
    CMD_MINE_ISSUES,
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


    def mine_repositories(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_REPOSITORIES
        )

        try:
            register_uuid() 
            queue = Queue(maxsize=20000)
            pool = ThreadedConnectionPool(0, 500, user="root", password="password", host="localhost", dbname="hf")
            
            dataset_list = list_datasets(with_details=False, with_community_datasets=True)
            dataset_list = [
                {
                    "repository_name": dataset, 
                    "repository_url": f"https://huggingface.co/datasets/{dataset}", 
                    "repository_type": ArtifactType.DATASET.value
                } 
                for dataset in dataset_list]
            
            model_list = huggingface_hub.list_models(full=False)
            model_list = [model.modelId for model in model_list]
            model_list = [
                {
                    "repository_name": model, 
                    "repository_url": f"https://huggingface.co/{model}", 
                    "repository_type": ArtifactType.MODEL.value
                } 
                for model in model_list]

            product_list = [
                    {
                        "repository_name": "huggingface/huggingface_hub", 
                        "repository_url": "https://github.com/huggingface/huggingface_hub", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "huggingface/transformers", 
                        "repository_url": "https://github.com/huggingface/transformers", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "huggingface/datasets", 
                        "repository_url": "https://github.com/huggingface/datasets", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "huggingface/tokenizers", 
                        "repository_url": "https://github.com/huggingface/tokenizers", 
                        "repository_type": ArtifactType.PRODUCT.value
                    }
                ]

            repositories = dataset_list + model_list + product_list

            random.shuffle(repositories)
            repositories = [repositories[x:x + 2500] for x in range(0, len(repositories), 2500)]
          
            
            processes = self._initiate_threads(queue, pool, repositories)

            self._start_parallelization(processes, queue)


        except ValueError as error:
            logger.errors(error)
            exit(1)


    def mine_issues(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_ISSUES
        )

        try:
            pass

        except ValueError as error:
            logger.error(str(error))
            exit(1)

    def _initiate_threads(self,
        queue: Queue, 
        pool: ThreadedConnectionPool,
        repositories: List[Dict[str, str]],) -> Tuple[List, List]:

        producers = []
        consumers = []

        for repository_group in range(len(repositories)):
            conn = pool.getconn()
            conn.set_session(autocommit=True)
            repository = GeneralRepository(conn)
            extractor = Extractor()
            writer = Writer(repository)

            producer = Producer(
                queue, 
                repositories[repository_group], 
            extractor
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
                if len(producer.repositories) == 0 and not producer.is_alive():                        
                    logger.info(f"Producer-{producer.pid} finished, joining")
                    logger.info(f"{len(producers)} left")
                    producers.remove(producer)
                    break

                if len(producer.repositories) > 0 and not producer.is_alive():

                        new_producer = Producer(
                            producer.queue, 
                            producer.repositories, 
                            producer.extractor, 
                        )
                        
                        producer.join() 
                        producers.remove(producer)
                        new_producer.start()
                        producers.append(new_producer)
                        break
                        
        
        queue.put(CONSUMER_KILL_SIG)

        for consumer in consumers:
            consumer.join()



