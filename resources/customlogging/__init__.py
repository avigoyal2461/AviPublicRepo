import os
import logging

logger = logging.getLogger(__name__)

if not os.path.exists('./logs'):
    os.mkdir('./logs')


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(name)s:%(message)s',
                    handlers=[logging.FileHandler(f'./logs/{__name__}.log'), logging.StreamHandler()])


class Logger:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def info(self, string):
        """
        Logs a string to info level.
        """
        self.logger.info(string)

    def warning(self, string):
        """
        Logs a string to warning level.
        """
        self.logger.warning(string)

    def error(self, string):
        """
        Logs a string to error level.
        """
        self.logger.error(string)