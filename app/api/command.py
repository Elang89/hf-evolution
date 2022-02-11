import argparse
from pprint import pprint
import sys
import os
import huggingface_hub
from numpy import insert
import psycopg2

from loguru import logger
from github import Github
from datasets import list_datasets
from pydriller import Repository

from app.resources.constants import (
    CMD_MINE_DATASETS,
    CMD_MINE_MODELS,
    COMMAND_LINE_OPTIONS, 
    COMMAND_LINE_DESCRIPTION,
    CMD_MINE_MODELS, 
    CMD_MINE_PRODUCTS
)
from app.services.dataset_respository import DatasetRepository
from app.models.dataset import DatasetDTO


class CommandLine(object):
    """This is the command line interface 
    for data extraction. 

    Args:
        object (object): default python object
    """

    def __init__(self):
        """constructor for CommandLine object.
        """
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
            conn =  psycopg2.connect(user="root", password="password", host="localhost", dbname="hf")
            data_repo = DatasetRepository(conn)

            dataset_list = list_datasets(with_details=False, with_community_datasets=True)
            dataset = dataset_list[0]

            url = f"https://huggingface.co/datasets/{dataset}"

            repo = Repository(url)

            insertion = DatasetDTO(dataset_name=dataset).dict()

            tup_value = str(tuple(insertion.values()))
            tup_value = tup_value[:-2] + tup_value[-1]
            values = [tup_value]

            print(values)


            data_repo.insert("datasets", list(insertion.keys()), values) 





        except ValueError as error:
            pass


    def mine_models(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_MODELS
        )

        try:
            model_info = huggingface_hub.model_info("gpt2")

            help(model_info.siblings[0])

        except ValueError as error:
            logger.error(str(error))
            exit(1)

    def mine_products(self):
        parser = argparse.ArgumentParser(
            description = CMD_MINE_PRODUCTS
        )

        try:
            access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
            g = Github(access_token)
            repository = g.get_repo("huggingface/datasets")
            single_commit = repository.get_commits()[0]

            commit = repository.get_commit(single_commit.sha)

            file_url = commit.files[0].contents_url

            client = httpx.Client()

            response = client.get(file_url)
            pprint(response.json())


        except ValueError as error:
            logger.error(str(error))
            exit(1)

