from multiprocessing import Process, Queue

from typing import Callable, List, Any

class ProcessManager(object):

    def __init__(self, num_processes: int, process_workflow: Callable, args: List[any], queue: Queue):
        self.process_list = [Process(target=process_workflow, args=tuple(args)) for _ in range(num_processes)]
        self.queue = queue 


    def initialize(self):
        pass

