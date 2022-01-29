import argparse
import sys
import os

from loguru import logger

from app.resources.constants import (
    COMMAND_LINE_OPTIONS, 
    COMMAND_LINE_DESCRIPTION,
    CMD_MINE_PRODUCTS
)


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

    def mine_products(self):

        parser = argparse.ArgumentParser(
            description = CMD_MINE_PRODUCTS
        )

        try:
            logger.info("stuff")


        except ValueError as error:
            logger.error(str(error))
            exit(1)

