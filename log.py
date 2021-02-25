#!/usr/bin/env python
import logging
import sys
    
def record():
    class StreamToLogger(object):
       """
       Fake file-like stream object that redirects writes to a logger instance.
       """
       def __init__(self, logger, log_level=logging.INFO):
          self.logger = logger
          self.log_level = log_level
          self.linebuf = ''
    
       def write(self, buf):
          for line in buf.rstrip().splitlines():
             self.logger.log(self.log_level, line.rstrip())
       
       def flush(self):
          pass
    
    logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s    %(levelname)s    %(name)s    %(message)s',
       filename="access.log",
       filemode='a'
    )
    
    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl
    
    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl
