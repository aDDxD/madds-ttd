import logging


class Logger:
    def __init__(self, name: str):
        """
        Initialize the Logger class with a logger name.

        :param name: Name of the logger (usually the class name).
        """
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_logger(self):
        """
        Return the configured logger instance.

        :return: Logger instance.
        """
        return self.logger
