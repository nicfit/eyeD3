import logging
from ..__about__ import __version__ as VERSION

DEFAULT_FORMAT = '%(name)s:%(levelname)s: %(message)s'
MAIN_LOGGER = "eyed3"

# Add some levels
logging.VERBOSE = logging.DEBUG + 1
logging.addLevelName(logging.VERBOSE, "VERBOSE")


class Logger(logging.Logger):
    """Base class for all loggers"""

    def __init__(self, name):
        logging.Logger.__init__(self, name)

        # Using propagation of child to parent, by default
        self.propagate = True
        self.setLevel(logging.NOTSET)

    def verbose(self, msg, *args, **kwargs):
        """Log \a msg at 'verbose' level, debug < verbose < info"""
        self.log(logging.VERBOSE, msg, *args, **kwargs)


def getLogger(name):
    og_class = logging.getLoggerClass()
    try:
        logging.setLoggerClass(Logger)
        return logging.getLogger(name)
    finally:
        logging.setLoggerClass(og_class)


# The main 'eyed3' logger
log = getLogger(MAIN_LOGGER)
log.debug("eyeD3 version " + VERSION)
del VERSION


def initLogging():
    """initialize the default logger with console output"""
    global log

    logging.basicConfig()

    # Don't propagate base 'eyed3'
    log.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
    log.addHandler(console_handler)

    log.setLevel(logging.ERROR)

    return log


LEVELS = (logging.DEBUG, logging.VERBOSE, logging.INFO,
          logging.WARNING, logging.ERROR, logging.CRITICAL)
