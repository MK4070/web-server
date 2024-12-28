import logging


def setup_loggers():
    common_logger = logging.getLogger("common")
    common_handler = logging.FileHandler("Logs/common.log", "w")
    common_handler.setFormatter(
        logging.Formatter("[%(asctime)s] - %(levelname)s - %(message)s")
    )
    common_logger.addHandler(common_handler)
    common_logger.setLevel(logging.INFO)

    def get_thread_logger(server_name):
        logger = logging.getLogger(server_name)
        handler = logging.FileHandler(f"Logs/{server_name}.log", "w")
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return logger

    return common_logger, get_thread_logger


common_logger, get_thread_logger = setup_loggers()
