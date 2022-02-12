import argparse
import sys
import huggingface_hub
import psycopg2

from loguru import logger
from datasets import list_datasets


from app.resources.constants import (
    CMD_MINE_DATASETS,
    CMD_MINE_MODELS,
    COMMAND_LINE_OPTIONS, 
    COMMAND_LINE_DESCRIPTION,
    CMD_MINE_MODELS, 
    CMD_MINE_PRODUCTS
)
from app.services.extractor import Extractor
from app.models.types import ArtifactType
from app.services.general_repository import GeneralRepository
from app.services.writer import Writer


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
            repository = GeneralRepository(conn)

            dataset_list = list_datasets(with_details=False, with_community_datasets=True)
            dataset = dataset_list[0]

            url = f"https://huggingface.co/datasets/{dataset}"

            extractor = Extractor()
            result = extractor.retrieve_data(url, dataset, ArtifactType.DATASET)

            writer = Writer(repository)
            writer.insert_data(result)


        except ValueError as error:
            print(error)


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
            pass


        except ValueError as error:
            logger.error(str(error))
            exit(1)

