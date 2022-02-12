from multiprocessing import Queue

from datasets import Dataset

from app.services.general_repository import DatasetRepository

def run_workflow(queue: Queue, repository: DatasetRepository):
    data = queue.get()
    
