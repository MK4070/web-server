import configparser
import os


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
            cls._config.read(
                os.path.join(os.path.dirname(__file__), "config.ini")
            )
        return cls._config
