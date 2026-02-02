"""File-digest formatter - human-readable format grouped by file"""

from collections import defaultdict
from typing import Any

from lib.log_format import LogFormat
from lib.log_formatters.base_log_formatter import BaseLogFormatter


class FileDigestFormatter(BaseLogFormatter):
    """Formats messages in file-digest format with line content and errors grouped by file"""

    def format(self, messages: list[dict[str, Any]]) -> str:
        """Format messages in file-digest format"""
        # Group messages by file
        by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
        unknown_messages: list[dict[str, Any]] = []

        for msg in messages:
            if msg["file"] == "<unknown>":
                unknown_messages.append(msg)
            else:
                by_file[msg["file"]].append(msg)

        output_lines = []

        # Format file-grouped messages
        for file_path in sorted(by_file.keys()):
            output_lines.append(f"\n{file_path}")
            for msg in sorted(by_file[file_path], key=lambda m: m["line_number"] or 0):
                line_num = msg["line_number"]
                if line_num:
                    output_lines.append(f"  (line {line_num}):")
                    # Placeholder for line content - would need source file reading
                    output_lines.append("    [line content would go here]")
                    output_lines.append(f"    ^-- {msg['rule']} ({msg['level'].name}): {msg['message']}")
                else:
                    output_lines.append("  (no line number):")
                    output_lines.append(f"    ^-- {msg['rule']} ({msg['level'].name}): {msg['message']}")
                output_lines.append("")

        # Format unknown messages (no file)
        if unknown_messages:
            output_lines.append("\n<unknown>")
            for msg in unknown_messages:
                output_lines.append(f"  ^-- {msg['rule']} ({msg['level'].name}): {msg['message']}")
                output_lines.append("")

        return "\n".join(output_lines)

    def get_format(self) -> LogFormat:
        """Return FILE_DIGEST format"""
        return LogFormat.FILE_DIGEST
