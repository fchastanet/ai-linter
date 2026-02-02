"""File-digest formatter - human-readable format grouped by file"""

from collections import defaultdict

from lib.log_format import LogFormat
from lib.log_formatters.base_log_formatter import BaseLogFormatter
from lib.log_formatters.rule_message import RuleMessage
from lib.log_level import RESET


class FileDigestFormatter(BaseLogFormatter):
    """Formats messages in file-digest format with line content and errors grouped by file"""

    def format(self, messages: list[RuleMessage]) -> str:
        """Format messages in file-digest format"""
        # Group messages by file
        by_file: dict[str, list[RuleMessage]] = defaultdict(list)
        unknown_messages: list[RuleMessage] = []
        for msg in messages:
            if msg.file == "<unknown>":
                unknown_messages.append(msg)
            else:
                by_file[msg.file].append(msg)

        output_lines = []

        # Format file-grouped messages
        for file_path in sorted(by_file.keys()):
            output_lines.append(f"\n{file_path}")
            for msg in sorted(by_file[file_path], key=lambda m: m.line_number or 0):
                line_num = msg.line_number
                color = msg.level.get_level_color()

                if line_num:
                    output_lines.append(f"  (line {line_num}):")
                    if msg.line_content:
                        output_lines.append(f"    {msg.line_content}")
                    output_lines.append(f"    ^-- {color}{msg.rule} ({msg.level.name}): {msg.message}{RESET}")
                else:
                    output_lines.append("  (no line number):")
                    output_lines.append(f"    ^-- {color}{msg.rule} ({msg.level.name}): {msg.message}{RESET}")
                output_lines.append("")

        # Format unknown messages (no file)
        if unknown_messages:
            output_lines.append("\n<unknown>")
            for msg in unknown_messages:
                output_lines.append(f"  ^-- {msg.rule} ({msg.level.name}): {msg.message}")
                output_lines.append("")

        return "\n".join(output_lines)

    def get_format(self) -> LogFormat:
        """Return FILE_DIGEST format"""
        return LogFormat.FILE_DIGEST
