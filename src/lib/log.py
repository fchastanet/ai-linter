import sys
from enum import Enum
from pathlib import Path
from typing import Any

from lib.log_format import LogFormat
from lib.log_formatters.formatter_factory import LogFormatterFactory

# ANSI color codes for console output
RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
BLUE = "\033[34m"
GRAY = "\033[90m"


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
    def __init__(self, level: LogLevel = LogLevel.INFO, format: LogFormat = LogFormat.FILE_DIGEST):
        self.level = level
        self.formatter = LogFormatterFactory.create(format)
        self.messages: list[dict[str, Any]] = []

    def set_level(self, level: LogLevel) -> None:
        """Set the logging level"""
        self.level = level

    def set_format(self, format: LogFormat) -> None:
        """Set the logging format"""
        self.formatter = LogFormatterFactory.create(format)

    def try_relative_path(self, file: str | Path | None) -> Path:
        """Try to convert file path to relative path"""
        if file is None:
            return Path("<unknown>")
        try:
            return Path(file).relative_to(Path.cwd())
        except ValueError:
            return Path(file)

    def log(
        self,
        level: LogLevel,
        rule: str,
        message: str,
        file: str | Path | None = None,
        line_number: int | None = None,
        **kwargs: str,
    ) -> None:
        """Log a message using the configured formatter"""
        if level.value > self.level.value:
            return
        # Store message for later formatting and output
        self._buffer_message(level, rule, message, file, line_number, kwargs)
        # For logfmt, also print immediately to stderr
        if self.formatter.get_format() == LogFormat.LOGFMT:
            self._print_logfmt_immediate(level, rule, message, file, line_number, kwargs)

    def _buffer_message(
        self,
        level: LogLevel,
        rule: str,
        message: str,
        file: str | Path | None,
        line_number: int | None,
        kwargs: dict[str, str],
    ) -> None:
        """Buffer a message for later formatting"""
        relative_path = str(self.try_relative_path(file)) if file else "<unknown>"
        self.messages.append(
            {
                "level": level,
                "rule": rule,
                "message": message,
                "file": relative_path,
                "line_number": line_number,
                "kwargs": kwargs,
            }
        )

    def _print_logfmt_immediate(
        self,
        level: LogLevel,
        rule: str,
        message: str,
        file: str | Path | None,
        line_number: int | None,
        kwargs: dict[str, str],
    ) -> None:
        """Print a message in logfmt format immediately to stderr"""
        relative_path = self.try_relative_path(file)
        if line_number:
            formatted_message = (
                f'level="{level.name}" rule="{rule}" path="{relative_path}" '
                f'line="{line_number}" message="{message}"'
            )
        else:
            formatted_message = f'level="{level.name}" rule="{rule}" path="{relative_path}" message="{message}"'
        for key, value in kwargs.items():
            formatted_message += f' {key}="{value}"'
        color = level.get_level_color()
        print(f"{color}{formatted_message}{RESET}", file=sys.stderr)

    def flush(self) -> None:
        """Output all buffered messages using the configured formatter"""
        if not self.messages:
            return
        output = self.formatter.format(self.messages)
        if output:
            print(output, file=sys.stderr)
        self.messages.clear()
