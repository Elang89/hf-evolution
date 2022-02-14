from multiprocessing import Pipe, Process
import traceback


class CustomProcess(Process): 

    def __init__(self, *args, **kwargs):
        Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = Pipe()
        self._exception = None
    
    def run(self):
        try:
            Process.run(self)
            self._cconn.send(None)
        except Exception as e: 
            tb = traceback.format_exc()
            self._cconn.send((e, tb))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception
