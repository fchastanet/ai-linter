"""Logfmt formatter - space-separated key=value pairs"""

from lib.log.log_colors import RESET
from lib.log.log_format import LogFormat
from lib.log.log_formatters.base_log_formatter import BaseLogFormatter
from lib.log.log_formatters.report_entry import ReportEntry
from lib.log.log_formatters.rule_message import RuleMessage
from lib.log.log_level import LogLevel


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
        sorted_entries = sorted(entries, key=lambda e: (e.get_severity(), e.file_path))

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

        # Add summary
        output += self._format_single_message(
            level=LogLevel.INFO,
            rule="summary",
            relative_path="<report>",
            line_number=None,
            message="",
            total_files=str(len(entries)),
            total_tokens=str(total_tokens),
            total_lines=str(total_lines),
            valid=str(valid_count),
            warnings=str(warning_count),
            errors=str(error_count),
        )

        return output

    def get_format(self) -> LogFormat:
        """Return LOGFMT format"""
        return LogFormat.LOGFMT
