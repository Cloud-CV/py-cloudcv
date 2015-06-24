import logging
from colorlog import ColoredFormatter

LOG_LEVEL = logging.DEBUG
logging.root.setLevel(LOG_LEVEL)
LOGFORMAT = "%(log_color)s[%(asctime)s] %(levelname)-8s | %(message)s%(reset)s"
formatter = ColoredFormatter(LOGFORMAT,datefmt="%H:%M:%s")
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)

def debug(message):
    log.debug(message)
def info(message):
    log.info(message)
def warn(message):
    log.warn(message)
def error( message):
    log.error(message)
def critical( message):
    log.critical(message)
    
class ArgumentError(Exception):
    """
    Used for error logging. 
    
    :param value: Each value indicates a different possible argument error.
    :type value: int
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if (self.value == 0):
            return 'Executable Not found. Possibly a typing error. Should be:\n1.) ImageStitch\n2.) VOCRelease5'
        if (self.value == 1):
            return 'Path to the folder containing images is not defined.\n Define it through -I parameter\n'
        if (self.value == 2):
            return 'Path to the output folder is not defined.\n Define it through -O parameter\n'



