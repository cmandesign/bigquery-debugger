# Create a file logger that writes log messages to a file
import logging
import os

home_path = os.path.expanduser('~')

logger = None

def get_logger():
    global logger
    if logger:
        return logger

    logger = logging.getLogger("file_logger")
    log_filename = os.path.abspath(os.path.join(home_path, 'BigDebug/' , 'logfile.log'))
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    file_handler = logging.FileHandler(log_filename)
    file_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return logger