import logging
import os
from pathlib import Path

ERROR_LOG_FILE = "errors.log"
STANDARD_LOG_FILE = "app.log"
formatter = logging.Formatter(fmt="[{levelname} {asctime}]: {message}", datefmt="%d-%m-%Y %H:%M:%S", style="{")


def create_log_file_handler(filename: str) -> logging.FileHandler:
    """This is only for the use by the file loggers."""
    path = Path().absolute().parent / "logs" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    handler = logging.FileHandler(path)
    handler.setFormatter(formatter)
    return handler


class StreamLogger():
    """This is used to log app events only to stdout for the users."""

    def __init__(self) -> None:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger = logging.getLogger("app")
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)


class EventsFileLogger():
    """This is used to log all app events to its corresponding log file for the users to describe app issues to the developers."""

    def __init__(self) -> None:
        handler = create_log_file_handler(STANDARD_LOG_FILE)
        self.logger = logging.getLogger("file")
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)


class ErrorFileLogger():
    """This is used to log errors to its corresponding log file for the users to directly see errors."""

    def __init__(self) -> None:
        handler = create_log_file_handler(ERROR_LOG_FILE)
        self.logger = logging.getLogger("file")
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
    

app_logger = StreamLogger().logger
file_logger = EventsFileLogger().logger
error_file_logger = ErrorFileLogger().logger
