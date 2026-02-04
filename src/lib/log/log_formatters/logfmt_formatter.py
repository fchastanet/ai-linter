"""Logfmt formatter - space-separated key=value pairs"""

from typing import Any

from lib.log.log_format import LogFormat
from lib.log.log_formatters.base_log_formatter import BaseLogFormatter
from lib.log.log_formatters.rule_message import RuleMessage


class LogfmtFormatter(BaseLogFormatter):
    """Formats messages as logfmt (space-separated key=value pairs)"""

    def format(self, messages: list[RuleMessage]) -> str:
        """Print a message in logfmt format immediately to stderr"""
        output = ""
        for msg in messages:
            output += self._format_single_message(
                level=msg.level,
                rule=msg.rule,
                relative_path=msg.file,
                line_number=msg.line_number,
                message=msg.message,
            )

        return output

    def _format_single_message(
        self,
        level: Any,
        rule: str,
        relative_path: str,
        line_number: int | None,
        message: str,
        **kwargs: str,
    ) -> str:
        """Print a single logfmt-formatted message to stderr"""
        RESET = "\033[0m"
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

        return f"{color}{formatted_message}{RESET}\n"

    def get_format(self) -> LogFormat:
        """Return LOGFMT format"""
        return LogFormat.LOGFMT
