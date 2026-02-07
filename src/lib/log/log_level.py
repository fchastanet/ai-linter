import logging
from enum import Enum

from lib.log.log_colors import BLUE, GRAY, RED, RESET, YELLOW


class LogLevel(Enum):
    """Log level enumeration"""

    ERROR = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3

    @classmethod
    def from_string(cls, value: str) -> "LogLevel":
        """Convert a string (or LogLevel) to a LogLevel enum (case-insensitive)."""

        if isinstance(value, cls):
            return value
        if value is None:
            return cls.INFO
        key = str(value).strip().upper()
        # Accept common synonyms
        synonyms = {
            "ERR": "ERROR",
            "WARN": "WARNING",
            "INFORMATION": "INFO",
            "INFOR": "INFO",
            "DBG": "DEBUG",
        }
        key = synonyms.get(key, key)
        if key in cls.__members__:
            return cls[key]
        # Fallback to INFO if unknown
        return cls.INFO

    def to_python_level(self) -> int:
        """Convert LogLevel to Python logging level"""
        level_map = {
            LogLevel.ERROR: logging.ERROR,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.INFO: logging.INFO,
            LogLevel.DEBUG: logging.DEBUG,
        }
        return level_map[self]

    @staticmethod
    def from_python_level(level: int) -> "LogLevel":
        """Convert Python logging level to LogLevel"""
        reverse_map = {
            logging.ERROR: LogLevel.ERROR,
            logging.WARNING: LogLevel.WARNING,
            logging.INFO: LogLevel.INFO,
            logging.DEBUG: LogLevel.DEBUG,
        }
        return reverse_map.get(level, LogLevel.INFO)

    def get_level_color(self) -> str:
        """Get color code for a given level"""

        if self.value == LogLevel.ERROR.value:
            return RED
        elif self.value == LogLevel.WARNING.value:
            return YELLOW
        elif self.value == LogLevel.INFO.value:
            return BLUE
        elif self.value == LogLevel.DEBUG.value:
            return GRAY
        else:
            return RESET

    def __str__(self) -> str:
        if self == LogLevel.ERROR:
            return "ERROR"
        elif self == LogLevel.WARNING:
            return "WARN"
        elif self == LogLevel.INFO:
            return "INFO"
        elif self == LogLevel.DEBUG:
            return "DEBUG"
        return ""
