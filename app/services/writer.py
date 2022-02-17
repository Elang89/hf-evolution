from typing import List

from app.models.event import Event
from app.services.general_repository import GeneralRepository


class Writer(object):

    def __init__(self, repository: GeneralRepository):
        self.repository = repository

    def insert_data(self, events: List[Event]) -> None:
        insert_events = [event.dict() for event in events]
        repositories = [event.pop("repository") for event in insert_events]
        authors = [event.pop("author") for event in insert_events]
        file_changes = [event.pop("file_change") for event in insert_events]
        commits = [event.pop("commit") for event in insert_events]

        self.repository.insert(file_changes)
        self.repository.insert(authors)
        self.repository.insert(commits)
        self.repository.insert(repositories)

