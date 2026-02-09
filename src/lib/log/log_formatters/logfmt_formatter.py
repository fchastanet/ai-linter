"""Logfmt formatter - space-separated key=value pairs"""

import os

from lib.log.log_colors import RESET
from lib.log.log_format import LogFormat
from lib.log.log_formatters.base_log_formatter import BaseLogFormatter
from lib.log.log_formatters.report_entry import ReportEntry
from lib.log.log_formatters.rule_message import RuleMessage
from lib.log.log_level import LogLevel


class LogfmtFormatter(BaseLogFormatter):
    """Formats messages as logfmt (space-separated key=value pairs)"""

    def format(self, entries: list[ReportEntry], messages: list[RuleMessage], start_time: os.times_result) -> str:
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

        output += self.format_report(entries)

        # Add summary
        summary_data = self.get_summary(entries, [], start_time)
        output += self._format_single_message(
            level=LogLevel.INFO,
            rule="summary",
            relative_path="<report>",
            line_number=None,
            message="",
            content_complexity_files_count=str(summary_data["content_complexity_files_count"]),
            content_complexity_total_tokens=str(summary_data["content_complexity_total_tokens"]),
            content_complexity_total_lines=str(summary_data["content_complexity_total_lines"]),
            content_complexity_valid_count=str(summary_data["content_complexity_valid_count"]),
            content_complexity_warning_count=str(summary_data["content_complexity_warning_count"]),
            content_complexity_error_count=str(summary_data["content_complexity_error_count"]),
            rule_warning_count=str(summary_data["rule_warning_count"]),
            rule_error_count=str(summary_data["rule_error_count"]),
            total_elapsed_time_seconds=str(summary_data["total_elapsed_time_seconds"]),
        )

        return output

    def _format_single_message(
        self,
        level: LogLevel,
        rule: str,
        relative_path: str,
        line_number: int | None,
        message: str,
        **kwargs: str,
    ) -> str:
        """Print a single logfmt-formatted message to stderr"""
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

    def format_report(self, entries: list[ReportEntry]) -> str:
        """Format report entries in logfmt format"""
        if not entries:
            return ""

        output = ""
        total_tokens = 0
        total_lines = 0
        valid_count = 0
        warning_count = 0
        error_count = 0

        # Sort by severity then by file path
        sorted_entries = self.get_entries_sorted_by_severity(entries)

        for entry in sorted_entries:
            # Determine level based on status
            if entry.status.startswith("❌"):
                level = LogLevel.ERROR
            elif entry.status.startswith("⚠️"):
                level = LogLevel.WARNING
            else:
                level = LogLevel.INFO

            output += self._format_single_message(
                level=level,
                rule="content-complexity",
                relative_path=entry.file_path,
                line_number=entry.line_number,
                message=f"Type: {entry.file_type}, Tokens: {entry.tokens}/{entry.max_tokens}, Lines: {entry.lines}/{entry.max_lines}, Status: {entry.status}",  # noqa: E501
            )

            total_tokens += entry.tokens
            total_lines += entry.lines

            if entry.status.startswith("✅"):
                valid_count += 1
            elif entry.status.startswith("⚠️"):
                warning_count += 1
            else:
                error_count += 1

        return output

    def get_format(self) -> LogFormat:
        """Return LOGFMT format"""
        return LogFormat.LOGFMT
