import logging
import os
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler

from config import PROJECT_ROOT


def retrieve_logger(logger_name, file_name="log"):
    try:
        logs_path = os.path.join(PROJECT_ROOT, "logs")
        if not os.path.isdir(logs_path):
            os.mkdir(logs_path)

        logs_folder_path = os.path.join(logs_path, logger_name)
        if not os.path.exists(logs_folder_path):
            os.mkdir(logs_folder_path)

        log_file_path = os.path.join(logs_folder_path, "{}.log".format(file_name))

        logger = logging.getLogger(file_name)

        stream_handler = logging.StreamHandler(sys.stdout)
        rotating_file_handler = TimedRotatingFileHandler(log_file_path)
        formatter = logging.Formatter(
            "[%(asctime)-15s] - [%(levelname)s - %(filename)s - %(threadName)s] %(message)s")

        for handler in [stream_handler, rotating_file_handler]:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(logging.DEBUG)
        return logger

    except Exception as err:
        print("Error occurred while retrieving the logger")
        print(err)
        print(get_traceback())


def get_traceback():
    return traceback.format_exc()
