import argparse
import random
import sys
from typing import Dict, List, Tuple
from uuid import uuid4
import huggingface_hub

from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import register_uuid
from loguru import logger
from datasets import list_datasets
from multiprocessing import Process, Queue


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
from app.utils.custom_process import CustomProcess
from app.workflows.producer_workflow import run_producer_workflow
from app.workflows.consumer_workflow import run_consumer_workflow


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


            dataset_list = [dataset_list[x:x + 30] for x in range(0, len(dataset_list), 30)]
            # print(len(dataset_list))
            # print(len(dataset_list[0]))

            processes = self._initiate_threads(dataset_list, pool, ArtifactType.DATASET, queue)

            # print(len(processes[0]))
            
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

        for counter, artifact_group in enumerate(range(len(artifact_list))):
            extractor = Extractor()

            producer = CustomProcess(
                target=run_producer_workflow, 
                args=(queue, artifact_list[artifact_group], extractor, artifact_type, counter))


            producers.append(producer)


        for counter in range(len(artifact_list ) * 2):
            conn = pool.getconn()
            repository = GeneralRepository(conn)
            writer = Writer(repository)

            consumer = CustomProcess(
                    target=run_consumer_workflow, 
                    args=(queue, writer, counter))
            
            consumers.append(consumer)
        
        return (producers, consumers)

    def _start_parallelization(self, processes: Tuple[List, List], queue: Queue):
        producers, consumers = processes

        for producer in producers:
            producer.start()

        for consumer in consumers: 
            consumer.start()

        while producers:
            for producer_num, producer in enumerate(producers):
                if not producer.is_alive():
                    logger.info(f"Producer-{producer_num} finished, joining")

                    producer.join()
                    producers.pop(producer_num)
                    break
        
        queue.put(CONSUMER_KILL_SIG)

        for consumer in consumers:
            consumer.join()



