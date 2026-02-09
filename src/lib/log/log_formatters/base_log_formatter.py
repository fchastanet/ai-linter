"""Abstract base class for log formatters"""

import os
from abc import ABC, abstractmethod

from pyparsing import Any

from lib.log.log_format import LogFormat
from lib.log.log_formatters.report_entry import ReportEntry
from lib.log.log_formatters.rule_message import RuleMessage
from lib.log.log_level import LogLevel


class BaseLogFormatter(ABC):
    """Abstract base class for log formatters"""

    @abstractmethod
    def format(self, entries: list[ReportEntry], messages: list[RuleMessage], start_time: os.times_result) -> str:
        """Format a list of messages for output"""
        pass

    @abstractmethod
    def get_format(self) -> LogFormat:
        """Return the LogFormat this formatter produces"""
        pass

    def get_summary(
        self, entries: list[ReportEntry], messages: list[RuleMessage], start_time: os.times_result
    ) -> dict[str, int]:
        """Returns a summary report from all entries and messages"""

        # compute number of warnings and errors
        content_complexity_warning_count = sum(1 for e in entries if e.status.startswith("⚠️"))
        content_complexity_error_count = sum(1 for e in entries if e.status.startswith("❌"))
        content_complexity_valid_count = sum(1 for e in entries if e.status.startswith("✅"))
        content_complexity_files_count = len(entries)
        content_complexity_total_tokens = sum(e.tokens for e in entries)
        content_complexity_total_lines = sum(e.lines for e in entries)

        # compute number of rules violated by severity
        rule_warning_count = sum(1 for m in messages if m.level == LogLevel.WARNING)
        rule_error_count = sum(1 for m in messages if m.level == LogLevel.ERROR)

        end_time = os.times()
        elapsed_time = end_time.elapsed - start_time.elapsed

        output_data: dict[str, Any] = {
            "content_complexity_files_count": content_complexity_files_count,
            "content_complexity_total_tokens": content_complexity_total_tokens,
            "content_complexity_total_lines": content_complexity_total_lines,
            "content_complexity_valid_count": content_complexity_valid_count,
            "content_complexity_warning_count": content_complexity_warning_count,
            "content_complexity_error_count": content_complexity_error_count,
            "rule_warning_count": rule_warning_count,
            "rule_error_count": rule_error_count,
            "total_elapsed_time_seconds": elapsed_time,
        }

        return output_data

    def get_entries_sorted_by_severity(self, entries: list[ReportEntry]) -> list[ReportEntry]:
        """Return entries sorted by severity (error, warning, valid) then by file path"""
        return sorted(entries, key=lambda e: (e.get_severity(), e.file_path))
