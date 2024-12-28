import logging
import os
from utils.config_reader import Config

config = Config.get_config()
log_directory = config.get("Server", "logDirectory")
os.makedirs(os.path.dirname(log_directory), exist_ok=True)


def setup_loggers():
    common_logger = logging.getLogger("common")
    common_handler = logging.FileHandler(f"{log_directory}/common.log", "w")
    common_handler.setFormatter(
        logging.Formatter("[%(asctime)s] - %(levelname)s - %(message)s")
    )
    common_logger.addHandler(common_handler)
    common_logger.setLevel(logging.INFO)

    def get_thread_logger(server_name):
        logger = logging.getLogger(server_name)
        handler = logging.FileHandler(
            f"../{log_directory}/{server_name}.log", "w"
        )
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return logger

    return common_logger, get_thread_logger


common_logger, get_thread_logger = setup_loggers()
