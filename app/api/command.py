import argparse
import os
import random
import sys
import psycopg2

from typing import Dict, List, Tuple, Union
from psycopg2.extras import register_uuid
from loguru import logger
from datasets import list_datasets
from huggingface_hub import list_models
from multiprocessing import Queue

from app.resources.constants import (
    CMD_MINE_REPOSITORIES,
    COMMAND_LINE_OPTIONS, 
    COMMAND_LINE_DESCRIPTION,
    CMD_MINE_ISSUES,
    CMD_MINE_RUNS,
    CONSUMER_KILL_SIG
)
from app.services.ci_extractor import CiExtractor
from app.services.ci_writer import CiWriter
from app.services.extractor import Extractor
from app.models.types import GithubRepositoryType, ArtifactType
from app.services.general_repository import GeneralRepository
from app.services.issue_extractor import IssueExtractor
from app.services.issue_writer import IssueWriter
from app.services.writer import Writer
from app.utils.alt_consumer import AltConsumer
from app.utils.alt_producer import AltProducer
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

    
    def test_cmd(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_REPOSITORIES
        )

        # model_list = list_models(full=False)
        # model_list = [model.modelId for model in model_list]
        dataset_list = list_datasets(with_details=False, with_community_datasets=True)
        self._compare_lists(dataset_list, 5432, ArtifactType.DATASET.value)


    def mine_datasets(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_REPOSITORIES
        )

        try:
            register_uuid() 
            queue = Queue(maxsize=20000)
            
            dataset_list = list_datasets(with_details=False, with_community_datasets=True)
            dataset_list = self._compare_lists(dataset_list, 5432, ArtifactType.DATASET.value)
        
            dataset_list = [
                { 
                    "repository_name": dataset,
                    "repository_url": f"https://huggingface.co/datasets/{dataset}", 
                    "repository_type": ArtifactType.DATASET.value
                } 
                for dataset in dataset_list]
            

            repositories = dataset_list
            random.shuffle(repositories)

            repositories = [repositories[x:x + 100] for x in range(0, len(repositories), 100)]
            
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
                    },
                    {
                        "repository_name": "tensorflow/tfx", 
                        "repository_url": "https://github.com/tensorflow/tfx", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "mlflow/mlflow", 
                        "repository_url": "https://github.com/mlflow/mlflow", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "pytorch/torchx", 
                        "repository_url": "https://github.com/pytorch/torchx", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "papercups-io/papercups", 
                        "repository_url": "https://github.com/papercups-io/papercups", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "nalgebra", 
                        "repository_url": "https://github.com/dimforge/nalgebra", 
                        "repository_type": ArtifactType.PRODUCT.value
                    },
                    {
                        "repository_name": "pyodide/pyodide", 
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

    def mine_issues(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_ISSUES
        )

        register_uuid() 
        queue = Queue(maxsize=20000)
        github_repo_list = [
                {
                    "repository_name": "huggingface/transformers", 
                    "repository_url": "https://github.com/huggingface/transformers", 
                    "repository_type": GithubRepositoryType.HFML.value
                },
                {
                    "repository_name": "huggingface/datasets", 
                    "repository_url": "https://github.com/huggingface/datasets", 
                    "repository_type": GithubRepositoryType.HFML.value
                },
                {
                    "repository_name": "huggingface/tokenizers", 
                    "repository_url": "https://github.com/huggingface/tokenizers", 
                    "repository_type": GithubRepositoryType.HFML.value
                },
                {
                    "repository_name": "tensorflow/tfx", 
                    "repository_url": "https://github.com/tensorflow/tfx", 
                    "repository_type": GithubRepositoryType.OTHERML.value
                },
                {
                    "repository_name": "mlflow/mlflow", 
                    "repository_url": "https://github.com/mlflow/mlflow", 
                    "repository_type": GithubRepositoryType.OTHERML.value
                },
                {
                    "repository_name": "pytorch/torchx", 
                    "repository_url": "https://github.com/pytorch/torchx", 
                    "repository_type": GithubRepositoryType.OTHERML.value
                },
                {
                    "repository_name": "papercups-io/papercups", 
                    "repository_url": "https://github.com/papercups-io/papercups", 
                    "repository_type": GithubRepositoryType.SOFTWARE.value
                },
                {
                    "repository_name": "dimforge/nalgebra", 
                    "repository_url": "https://github.com/dimforge/nalgebra", 
                    "repository_type": GithubRepositoryType.SOFTWARE.value
                },
                {
                    "repository_name": "pyodide/pyodide", 
                    "repository_url": "https://github.com/pyodide/pyodide", 
                    "repository_type": GithubRepositoryType.SOFTWARE.value
                },
            ]

        processes = self._initiate_threads_alternate(queue, github_repo_list, 5435, IssueExtractor, IssueWriter)
        
        self._start_parallelization(processes)
        self._monitor_producers(queue, processes)

    def mine_runs(self):

        parser = argparse.ArgumentParser(
            description = CMD_MINE_RUNS
        )

        register_uuid() 
        queue = Queue(maxsize=20000)
        github_repo_list = [
                {
                    "repository_name": "huggingface/transformers", 
                    "repository_url": "https://github.com/huggingface/transformers", 
                    "repository_type": GithubRepositoryType.HFML.value
                },
                {
                    "repository_name": "huggingface/datasets", 
                    "repository_url": "https://github.com/huggingface/datasets", 
                    "repository_type": GithubRepositoryType.HFML.value
                },
                {
                    "repository_name": "huggingface/tokenizers", 
                    "repository_url": "https://github.com/huggingface/tokenizers", 
                    "repository_type": GithubRepositoryType.HFML.value
                },
                {
                    "repository_name": "tensorflow/tfx", 
                    "repository_url": "https://github.com/tensorflow/tfx", 
                    "repository_type": GithubRepositoryType.OTHERML.value
                },
                {
                    "repository_name": "mlflow/mlflow", 
                    "repository_url": "https://github.com/mlflow/mlflow", 
                    "repository_type": GithubRepositoryType.OTHERML.value
                },
                {
                    "repository_name": "pytorch/torchx", 
                    "repository_url": "https://github.com/pytorch/torchx", 
                    "repository_type": GithubRepositoryType.OTHERML.value
                },
                {
                    "repository_name": "papercups-io/papercups", 
                    "repository_url": "https://github.com/papercups-io/papercups", 
                    "repository_type": GithubRepositoryType.SOFTWARE.value
                },
                {
                    "repository_name": "dimforge/nalgebra", 
                    "repository_url": "https://github.com/dimforge/nalgebra", 
                    "repository_type": GithubRepositoryType.SOFTWARE.value
                },
                {
                    "repository_name": "pyodide/pyodide", 
                    "repository_url": "https://github.com/pyodide/pyodide", 
                    "repository_type": GithubRepositoryType.SOFTWARE.value
                },
            ]

        processes = self._initiate_threads_alternate(queue, github_repo_list, 5435, CiExtractor, CiWriter)
        
        self._start_parallelization(processes)
        self._monitor_producers(queue, processes)



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
            conn3 = psycopg2.connect(host="localhost", port=port, user="root", password="password", dbname="hf")
            conn3.set_session(autocommit=True)
            repository1 = GeneralRepository(conn1)
            repository2 = GeneralRepository(conn2)
            repository3 = GeneralRepository(conn3)
            extractor = Extractor()
            writer1 = Writer(repository1)
            writer2 = Writer(repository2)
            writer3 = Writer(repository3)

            work_list = repositories[repository_group][:]

            producer = Producer(
                queue, 
                extractor,
                work_list
            )

            consumer1 = Consumer(queue, writer1)
            consumer2 = Consumer(queue, writer2)
            consumer3 = Consumer(queue, writer3)
            
            consumers.append(consumer1)
            consumers.append(consumer2)
            consumers.append(consumer3)
            producers.append(producer)

        
        return (producers, consumers)

    
    def _initiate_threads_alternate(
            self, 
            queue: Queue, 
            repositories: List[Dict[str, str]],
            port: int, 
            extractor_class: Union[IssueExtractor, CiExtractor],
            writer_class: Union[IssueWriter, CiWriter]
        ) -> None: 
        access_token = os.environ.get("GITHUB_ACCESS_TOKEN")

        producers = []
        consumers = []
        
        for repository in repositories:
            conn1 = psycopg2.connect(host="localhost", port=port, user="root", password="password", dbname="hf")
            conn1.set_session(autocommit=True)
            conn2 = psycopg2.connect(host="localhost", port=port, user="root", password="password", dbname="hf")
            conn2.set_session(autocommit=True)
            conn3 = psycopg2.connect(host="localhost", port=port, user="root", password="password", dbname="hf")
            conn3.set_session(autocommit=True)
            db_repository1 = GeneralRepository(conn1)
            db_repository2 = GeneralRepository(conn2)
            db_repository3 = GeneralRepository(conn3)

            extractor = extractor_class(access_token, repository, db_repository1)
            writer1  = writer_class(db_repository2)
            writer2 = writer_class(db_repository3)

            producer = AltProducer(queue, extractor, repository)
            consumer1 = AltConsumer(queue, writer1)
            consumer2 = AltConsumer(queue, writer2)

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


    def _compare_lists(self, artifact_list: List[str], port: int, artifact_type: int) -> List[str]:
        conn =  psycopg2.connect(host="localhost", port=port, user="root", password="password", dbname="hf")
        artifact_set = set(artifact_list)
        sql = f"SELECT DISTINCT repository_name FROM hf_repositories WHERE repository_type = {artifact_type}"

        cursor = conn.cursor()
        cursor.execute(sql)

        result = cursor.fetchall()
        result = set([item[0] for item in result])

        difference = artifact_set - result

        print(len(artifact_list))
        print(len(result))
        print(len(difference))

        return difference
        


