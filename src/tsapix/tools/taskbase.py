import signal
from contextlib import contextmanager
import logging
import logging.config

class TimeoutException(Exception): pass

@contextmanager
def exe_time_limit(secs):
    def signal_handler(signum, frame):
        raise TimeoutException("Time Out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(secs)
    try:
        yield
    finally:
        signal.alarm(0)

        
def free_memory(objlist):
    import gc
    if gc.collect() > 0:
        try:
            for xobj in objlist:
                del xobj
            _m = gc.collect()
            logging.info("Freed memory to {}".format(_m))
        except:
            pass