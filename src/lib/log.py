import sys
from enum import Enum
from pathlib import Path

# ANSI color codes for console output
RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
BLUE = "\033[34m"
GRAY = "\033[90m"


class LogLevel(Enum):
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


class Logger:
    def __init__(self, level: LogLevel = LogLevel.INFO):
        self.level = level

    def set_level(self, level: LogLevel) -> None:
        """Set the logging level"""
        self.level = level

    def try_relative_path(self, file: str | Path | None) -> Path:
        """Try to convert file path to relative path"""
        if file is None:
            return Path("<unknown>")
        try:
            return Path(file).relative_to(Path.cwd())
        except ValueError:
            return Path(file)

    def _format_message(
        self, level: LogLevel, rule: str, message: str, file: str | Path | None, line_number: int | None = None
    ) -> str:
        """Format message for console output"""
        relative_path = self.try_relative_path(file)
        if line_number:
            return f'level="{level}" rule="{rule}" path="{relative_path}" line="{line_number}" message="{message}"'
        else:
            return f'level="{level}" rule="{rule}" path="{relative_path}" message="{message}"'

    def log(
        self,
        level: LogLevel,
        rule: str,
        message: str,
        file: str | Path | None = None,
        line_number: int | None = None,
        **kwargs: str,
    ) -> None:
        """Display message with color coding"""
        if level.value > self.level.value:
            return
        formatted_message = self._format_message(level, rule, message, file, line_number)
        for key, value in kwargs.items():
            formatted_message += f' {key}="{value}"'
        # Print on stderr
        color = level.get_level_color()
        print(f"{color}{formatted_message}{RESET}", file=sys.stderr)
