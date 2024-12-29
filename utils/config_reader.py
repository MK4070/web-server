import configparser
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

while not os.path.exists(os.path.join(ROOT_DIR, "requirements.txt")):
    ROOT_DIR = os.path.dirname(ROOT_DIR)


class Config:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_config(cls):
        """Get the singleton instance and load the config."""
        if cls._config is None:
            cls._config = configparser.ConfigParser()
            cls._config.read(os.path.join(ROOT_DIR, "config", "config.ini"))
        return cls._config
