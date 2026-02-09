"""YAML formatter - structured YAML output"""

import os
from collections import defaultdict
from typing import Any

import yaml

from lib.log.log_format import LogFormat
from lib.log.log_formatters.base_log_formatter import BaseLogFormatter
from lib.log.log_formatters.report_entry import ReportEntry
from lib.log.log_formatters.rule_message import RuleMessage


class YamlFormatter(BaseLogFormatter):
    """Formats messages in YAML structure grouped by file"""

    def format(self, entries: list[ReportEntry], messages: list[RuleMessage], start_time: os.times_result) -> str:
        """Format messages in YAML format"""

        # Group messages by file
        by_file: dict[str, list[RuleMessage]] = defaultdict(list)
        unknown_messages: list[RuleMessage] = []

        for msg in messages:
            if msg.file == "<unknown>":
                unknown_messages.append(msg)
            else:
                by_file[msg.file].append(msg)

        output_data: dict[str, Any] = {"files": {}}

        # Add file-grouped messages
        for file_path in sorted(by_file.keys()):
            file_messages = []
            for msg in sorted(by_file[file_path], key=lambda m: m.line_number or 0):
                file_msg: dict[str, Any] = {
                    "level": msg.level.name,
                    "rule": msg.rule,
                    "message": msg.message,
                }
                if msg.line_number:
                    file_msg["line"] = msg.line_number
                file_messages.append(file_msg)
            output_data["files"][file_path] = file_messages

        # Add unknown messages
        if unknown_messages:
            unknown_file_messages = []
            for msg in unknown_messages:
                unknown_file_messages.append(
                    {
                        "level": msg.level.name,
                        "rule": msg.rule,
                        "message": msg.message,
                    }
                )
            output_data["files"]["<unknown>"] = unknown_file_messages

        output_data["report"] = self._get_report_data(entries)
        output_data["summary"] = self.get_summary(entries, messages, start_time)

        # Convert to YAML
        try:
            return yaml.dump(output_data, default_flow_style=False, sort_keys=False)
        except ImportError:
            raise RuntimeError("PyYAML is not installed, cannot format logs as YAML")

    def _get_report_data(self, entries: list[ReportEntry]) -> list[dict[str, Any]]:
        """Format report entries in YAML format"""
        if not entries:
            return []

        # Sort by severity then by file path
        sorted_entries = self.get_entries_sorted_by_severity(entries)

        total_tokens = 0
        total_lines = 0
        valid_count = 0
        warning_count = 0
        error_count = 0

        report_data = []
        for entry in sorted_entries:
            report_data.append(
                {
                    "file_path": entry.file_path,
                    "line_number": entry.line_number,
                    "type": entry.file_type,
                    "tokens": entry.tokens,
                    "max_tokens": entry.max_tokens,
                    "lines": entry.lines,
                    "max_lines": entry.max_lines,
                    "status": entry.status,
                }
            )

            total_tokens += entry.tokens
            total_lines += entry.lines

            if entry.status.startswith("✅"):
                valid_count += 1
            elif entry.status.startswith("⚠️"):
                warning_count += 1
            else:
                error_count += 1

        return report_data

    def get_format(self) -> LogFormat:
        """Return YAML format"""
        return LogFormat.YAML
