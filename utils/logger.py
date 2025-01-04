__all__ = ["common_logger", "get_server_logger"]

import logging
import os
from utils.config_reader import Config, ROOT_DIR


def setup_loggers():
    config = Config.get_config()
    LOG_DIR = os.path.join(ROOT_DIR, config.get("Server", "log_directory"))
    os.makedirs(LOG_DIR, exist_ok=True)

    common_logger = logging.getLogger("common")
    common_handler = logging.FileHandler(
        os.path.join(LOG_DIR, "common.log"), "w"
    )
    common_handler.setFormatter(
        logging.Formatter("[%(asctime)s] - %(levelname)s - %(message)s")
    )
    common_logger.addHandler(common_handler)
    common_logger.setLevel(logging.INFO)

    def get_server_logger(server_name):
        logger = logging.getLogger(server_name)
        handler = logging.FileHandler(
            os.path.join(LOG_DIR, f"{server_name}.log"), "w"
        )
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return logger

    return common_logger, get_server_logger


common_logger, get_server_logger = setup_loggers()
