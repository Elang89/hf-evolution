import argparse
import random
import sys
import time
import psycopg2

from typing import Any, Dict, List, Tuple, Union
from psycopg2.extras import register_uuid
from loguru import logger
from datasets import list_datasets
from huggingface_hub import list_models
from multiprocessing import Queue

from py import process


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


    def mine_datasets(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_REPOSITORIES
        )

        try:
            register_uuid() 
            queue = Queue(maxsize=20000)
            
            dataset_list = list_datasets(with_details=False, with_community_datasets=True)
            dataset_list = [
                { 
                    "repository_name": dataset,
                    "repository_url": f"https://huggingface.co/datasets/{dataset}", 
                    "repository_type": ArtifactType.DATASET.value
                } 
                for dataset in dataset_list]
            

            repositories = dataset_list
            random.shuffle(repositories)

            repositories = [repositories[x:x + 250] for x in range(0, len(repositories), 250)]
            
            processes = self._initiate_threads(queue, repositories, 5432)

            self._start_parallelization(processes)
            self._monitor_producers(queue, processes)


        except ValueError as error:
            logger.error(error)
            exit(1)


    def mine_models(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_ISSUES
        )

        try:
            register_uuid() 
            queue = Queue(maxsize=20000)

            model_list = list_models(full=False)
            model_list = [model.modelId for model in model_list]
            model_list = random.sample(model_list, 3000)
            model_list = [
                {
                    "repository_name": model, 
                    "repository_url": f"https://huggingface.co/{model}", 
                    "repository_type": ArtifactType.MODEL.value
                } 
                for model in model_list]

            repositories =  model_list 


            repositories = [repositories[x:x + 250] for x in range(0, len(repositories), 250)]

            random.shuffle(repositories)
            
            processes = self._initiate_threads(queue, repositories, 5433)

            self._start_parallelization(processes)
            self._monitor_producers(queue, processes)

        except ValueError as error:
            logger.error(str(error))
            exit(1)

    def mine_products(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_ISSUES
        )

        try:
            register_uuid() 
            queue = Queue(maxsize=20000)

 
            product_list = [
                    # {
                    #     "repository_name": "huggingface/transformers", 
                    #     "repository_url": "https://github.com/huggingface/transformers", 
                    #     "repository_type": ArtifactType.PRODUCT.value
                    # },
                    # {
                    #     "repository_name": "huggingface/datasets", 
                    #     "repository_url": "https://github.com/huggingface/datasets", 
                    #     "repository_type": ArtifactType.PRODUCT.value
                    # },
                    # {
                    #     "repository_name": "huggingface/tokenizers", 
                    #     "repository_url": "https://github.com/huggingface/tokenizers", 
                    #     "repository_type": ArtifactType.PRODUCT.value
                    # },
                    # {
                    #     "repository_name": "tfx", 
                    #     "repository_url": "https://github.com/tensorflow/tfx", 
                    #     "repository_type": ArtifactType.PRODUCT.value
                    # },
                    # {
                    #     "repository_name": "mlflow", 
                    #     "repository_url": "https://github.com/mlflow/mlflow", 
                    #     "repository_type": ArtifactType.PRODUCT.value
                    # },
                    # {
                    #     "repository_name": "torchx", 
                    #     "repository_url": "https://github.com/pytorch/torchx", 
                    #     "repository_type": ArtifactType.PRODUCT.value
                    # },
                    {
                        "repository_name": "realtime", 
                        "repository_url": "https://github.com/supabase/realtime", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "nalgebra", 
                        "repository_url": "https://github.com/dimforge/nalgebra", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "pyodide", 
                        "repository_url": "https://github.com/pyodide/pyodide", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                ]

            repositories =  product_list 
            repositories = [repositories[x:x + 1] for x in range(0, len(repositories), 1)]

            random.shuffle(repositories)
            
            processes = self._initiate_threads(queue, repositories, 5434)

            self._start_parallelization(processes)
            self._monitor_producers(queue, processes)

        except ValueError as error:
            logger.error(str(error))
            exit(1)

    def _initiate_threads(self, 
            queue: Queue,
            repositories: List[Dict[str, str]],
            port: int
        ) -> List[Producer]:

        producers = []
        consumers = []

        for repository_group in range(len(repositories)):
            conn1 = psycopg2.connect(host="localhost", port=port, user="root", password="password", dbname="hf")
            conn1.set_session(autocommit=True)
            conn2 = psycopg2.connect(host="localhost", port=port, user="root", password="password", dbname="hf")
            conn2.set_session(autocommit=True)
            repository1 = GeneralRepository(conn1)
            repository2 = GeneralRepository(conn2)
            extractor = Extractor()
            writer1 = Writer(repository1)
            writer2 = Writer(repository2)

            work_list = repositories[repository_group][:]

            producer = Producer(
                queue, 
                extractor,
                work_list
            )

            consumer1 = Consumer(queue, writer1)
            consumer2 = Consumer(queue, writer2)

            
            consumers.append(consumer1)
            consumers.append(consumer2)
            producers.append(producer)

        
        return (producers, consumers)

    def _start_parallelization(self, processes: Tuple[List, List]) -> None:

        producers, consumers = processes

        for producer in producers:
            producer.start()

        for consumer in consumers: 
            consumer.start()

    
    def _monitor_producers(self, queue: Queue, processes: Tuple[List, List]) -> None:
        producers, consumers = processes

        while producers:
            for producer in producers:
                if not producer.is_alive():
                    logger.info(f"Producer-{producer.pid} is finished, terminating and joining")
                    producer.join()
                    producers.remove(producer)

                        
        queue.put(CONSUMER_KILL_SIG)

        for consumer in consumers:
            consumer.join()

