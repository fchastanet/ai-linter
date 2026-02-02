"""Logfmt formatter - space-separated key=value pairs"""

from typing import Any

from lib.log_format import LogFormat
from lib.log_formatters.base_log_formatter import BaseLogFormatter


class LogfmtFormatter(BaseLogFormatter):
    """Formats messages as logfmt (space-separated key=value pairs)"""

    def format(self, messages: list[dict[str, Any]]) -> str:
        """Format messages as logfmt - already printed immediately, so return empty"""
        return ""

    def get_format(self) -> LogFormat:
        """Return LOGFMT format"""
        return LogFormat.LOGFMT
