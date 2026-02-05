import logging
import sys
from pathlib import Path
from typing import Any, Mapping, Tuple, Union

from lib.log.log_format import LogFormat
from lib.log.log_formatters.formatter_factory import LogFormatterFactory
from lib.log.log_formatters.rule_message import RuleMessage
from lib.log.log_level import LogLevel


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    blue = "\x1b[34;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def format(self, record):  # type: ignore[no-untyped-def]
        level = LogLevel.from_python_level(record.levelno)
        color = level.get_level_color()
        levelPad = f"{str(level):<5}"
        log_fmt = f"{color}{levelPad} - %(message)s{self.reset}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    """Logger with support for two handler types: general messages and rule-based messages"""

    def __init__(self, level: LogLevel = LogLevel.INFO, format: LogFormat = LogFormat.FILE_DIGEST):
        self.level = level
        self.log_format = format
        self.messages: list[RuleMessage] = []

        # Create internal Python logger
        self.general_logger = logging.getLogger("ai_linter")
        self.general_logger.setLevel(level.to_python_level())
        self.general_logger.handlers.clear()  # Clear any existing handlers

        # Add handlers to logger
        self.general_handler = logging.StreamHandler(sys.stderr)
        self.general_handler.setFormatter(CustomFormatter())
        self.general_logger.addHandler(self.general_handler)

        self.formatter = LogFormatterFactory.create(self.log_format)

    def set_level(self, level: LogLevel) -> None:
        """Set the logging level"""
        self.level = level
        self.general_logger.setLevel(level.to_python_level())
        self.general_handler.setLevel(level.to_python_level())

    def set_format(self, format: LogFormat) -> None:
        """Set the logging format"""
        self.log_format = format
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
        message: str,
        args: Union[Tuple[Any, ...], Mapping[str, Any]] = (),
    ) -> None:
        """Log a general message (operational log without rule code).

        Args:
            level: LogLevel enum value
            message: The message to log
            args: Additional arguments for the log message

        Note: This should be used for general operational messages like debug info,
        progress messages, etc. For validation errors with rule codes, use logRule() instead.
        """
        if level.value > self.level.value:
            return

        # Create log record without rule_code to route to general handler
        record = logging.LogRecord(
            name="ai_linter",
            level=level.to_python_level(),
            pathname="",
            lineno=0,
            msg=message,
            exc_info=None,
            func=None,
            sinfo=None,
            args=args,
        )
        self.general_logger.handle(record)

    def logRule(
        self,
        level: LogLevel,
        rule: str,
        message: str,
        file: str | Path | None = None,
        line_number: int | None = None,
        line_content: str | None = None,
        **kwargs: str,
    ) -> None:
        """Log a rule-based message (validation error with rule code).

        Args:
            level: LogLevel enum value
            rule: Rule code/identifier (e.g., "invalid-name-format")
            message: The error message
            file: Optional file path where the error occurred
            line_number: Optional line number in the file
            **kwargs: Additional key-value pairs for structured logging

        Note: This should be used for all validation rule violations.
        For general operational messages, use log() instead.
        """
        if level.value > self.level.value:
            return

        # Buffer message for later formatting
        relative_path = str(self.try_relative_path(file)) if file else "<unknown>"
        self.messages.append(
            RuleMessage(
                level=level,
                rule=rule,
                message=message,
                file=relative_path,
                line_number=line_number,
                line_content=line_content,
                **kwargs,
            )
        )

        # For logfmt, also print immediately to stderr
        if self.log_format == LogFormat.LOGFMT:
            self.flush()

    def flush(self) -> None:
        """Output all buffered rule messages using the configured formatter"""
        if not self.messages:
            return
        output = self.formatter.format(self.messages)
        if output != "":
            print(output, file=sys.stdout, end="")
        self.messages.clear()
