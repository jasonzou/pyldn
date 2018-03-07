"""
CherryPy WebServer starter.
"""

__author__    = 'Jason Zou <jason.zou@gmal.com>'
__contact__   = 'jason.zou@gmal.com'
__date__      = '7 March 2018'

import sys
import logging 

#Set logging handlers for the first time
#import logconfig

from lib import LDNReceiverServer

# Logging
LOG_FORMAT = '%(asctime)-15s [%(levelname)s] (%(module)s.%(funcName)s) %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)

def main():
  try:
    log.info("hello")
    LDNReceiver = LDNReceiverServer()
    log.info("helloddd")
    LDNReceiver.start()
    return 0
  except:
    # Dump callstack to log and exit with -1
    log.exception('Unexpected exception occured.') 
    return -1
  
if __name__ == '__main__':
      sys.exit(main())
