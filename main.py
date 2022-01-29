from setuptools import Command
from dotenv import load_dotenv

from app.api.command import CommandLine

def main():
    load_dotenv()
    CommandLine()


if __name__ == "__main___":
    main()