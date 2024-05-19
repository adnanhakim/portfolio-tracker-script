"""
utils.logger
~~~~~~~~~~~~~~

This module contains a function to setup logger.

"""

import logging
from enum import Enum


# Define color codes
class Color(Enum):
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    DIM_CYAN = "\033[36;2;180;180;180m"


# Custom formatter to add colors to log messages
class ColoredFormatter(logging.Formatter):
    """A class to set colours to logs"""

    def format(self, record) -> str:
        # Add color codes based on log level
        if record.levelno == logging.DEBUG:
            log_msg = f"{Color.DIM_CYAN.value}[{record.levelname}] {record.getMessage()}{Color.RESET.value}"
        elif record.levelno == logging.INFO:
            log_msg = f"{Color.GREEN.value}[{record.levelname}] {record.getMessage()}{Color.RESET.value}"
        elif record.levelno == logging.WARNING:
            log_msg = f"{Color.YELLOW.value}[{record.levelname}] {record.getMessage()}{Color.RESET.value}"
        elif record.levelno == logging.ERROR or record.levelno == logging.CRITICAL:
            log_msg = f"{Color.RED.value}[{record.levelname}] {record.getMessage()}{Color.RESET.value}"
        else:
            log_msg: str | logging.Any = record.msg

        # Return the log message with color codes
        return log_msg


# Setup logging
def setup_logging(verbose=False):
    level: int = logging.DEBUG if verbose else logging.INFO

    # Create logger and set level to INFO
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(level)

    # Create console handler and set level to INFO
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter and add it to the handler
    formatter = ColoredFormatter()
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)
