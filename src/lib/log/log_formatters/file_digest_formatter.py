"""File-digest formatter - human-readable format grouped by file"""

import os
from collections import defaultdict

from lib.log.log_colors import RESET
from lib.log.log_format import LogFormat
from lib.log.log_formatters.base_log_formatter import BaseLogFormatter
from lib.log.log_formatters.report_entry import ReportEntry
from lib.log.log_formatters.rule_message import RuleMessage
from lib.log.log_level import LogLevel
from lib.table.tabulate_adapter import TabulateAdapter


class FileDigestFormatter(BaseLogFormatter):
    """Formats messages in file-digest format with line content and errors grouped by file"""

    def format(self, entries: list[ReportEntry], messages: list[RuleMessage], start_time: os.times_result) -> str:
        """Format messages in file-digest format"""
        # Group messages by file
        by_file: dict[str, list[RuleMessage]] = defaultdict(list)
        unknown_messages: list[RuleMessage] = []
        for msg in messages:
            if msg.file == "<unknown>":
                unknown_messages.append(msg)
            else:
                by_file[msg.file].append(msg)

        rules_output_lines = []

        # Format file-grouped messages
        for file_path in sorted(by_file.keys()):
            rules_output_lines.append(f"\n{file_path}")
            for msg in sorted(by_file[file_path], key=lambda m: m.line_number or 0):
                line_num = msg.line_number
                color = msg.level.get_level_color()

                if line_num:
                    rules_output_lines.append(f"  (line {line_num}):")
                    if msg.line_content:
                        rules_output_lines.append(f"    {msg.line_content}")
                    rules_output_lines.append(f"    ^-- {color}{msg.rule} ({msg.level.name}): {msg.message}{RESET}")
                else:
                    rules_output_lines.append("  (no line number):")
                    rules_output_lines.append(f"    ^-- {color}{msg.rule} ({msg.level.name}): {msg.message}{RESET}")
                rules_output_lines.append("")

        # Format unknown messages (no file)
        if unknown_messages:
            rules_output_lines.append("\n<unknown>")
            for msg in unknown_messages:
                rules_output_lines.append(f"  ^-- {msg.rule} ({msg.level.name}): {msg.message}")
                rules_output_lines.append("")

        # Generate table using tabulate adapter
        sorted_entries = self.get_entries_sorted_by_severity(entries)
        content_length_output_lines = TabulateAdapter.generate_report_table(sorted_entries)
        # compute first line length
        lines = content_length_output_lines.splitlines() if content_length_output_lines else []
        banner_width = max((len(line) for line in lines), default=80)

        # Format a summary report from all entries
        data = self.get_summary(entries, messages, start_time)
        rule_warning_count = data["rule_warning_count"]
        rule_error_count = data["rule_error_count"]
        rule_warning_color = LogLevel.WARNING.get_level_color() if rule_warning_count > 0 else ""
        rule_error_color = LogLevel.ERROR.get_level_color() if rule_error_count > 0 else ""

        summary_output_lines = TabulateAdapter.display_table(
            tabular_data=[
                [
                    "Content Complexity Warnings",
                    f"{data['content_complexity_warning_count']}/{data['content_complexity_files_count']}",
                ],
                [
                    "Content Complexity Errors",
                    f"{data['content_complexity_error_count']}/{data['content_complexity_files_count']}",
                ],
                [
                    "Content Complexity Valid",
                    f"{data['content_complexity_valid_count']}/{data['content_complexity_files_count']}",
                ],
                # format in yellow if warnings exceed threshold
                [
                    "Rule Warnings",
                    f"{rule_warning_color}{rule_warning_count}{RESET}",
                ],
                [
                    "Rule Errors",
                    f"{rule_error_color}{rule_error_count}{RESET}",
                ],
                ["Total Elapsed Time (seconds)", f"{data['total_elapsed_time_seconds']:.2f}"],
            ],
            headers=["Metric", "Value"],
        )

        output_lines = []
        if rules_output_lines:
            output_lines.extend(["\n" + "=" * banner_width, "Rule Violations", "=" * banner_width])
            output_lines.extend(rules_output_lines)
        if content_length_output_lines:
            output_lines.extend(["\n" + "=" * banner_width, "Content Length Validation Report", "=" * banner_width, ""])
            output_lines.append(content_length_output_lines)
        if summary_output_lines:
            output_lines.extend(
                [
                    "\n" + "=" * banner_width,
                    "Content Length Validation Report",
                    "=" * banner_width,
                ]
            )
            output_lines.append(summary_output_lines)

        return "\n".join(output_lines) + "\n"

    def get_format(self) -> LogFormat:
        """Return FILE_DIGEST format"""
        return LogFormat.FILE_DIGEST
