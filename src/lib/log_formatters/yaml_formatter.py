"""YAML formatter - structured YAML output"""

from collections import defaultdict
from typing import Any

import yaml

from lib.log_format import LogFormat
from lib.log_formatters.base_log_formatter import BaseLogFormatter


class YamlFormatter(BaseLogFormatter):
    """Formats messages in YAML structure grouped by file"""

    def format(self, messages: list[dict[str, Any]]) -> str:
        """Format messages in YAML format"""

        # Group messages by file
        by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
        unknown_messages: list[dict[str, Any]] = []

        for msg in messages:
            if msg["file"] == "<unknown>":
                unknown_messages.append(msg)
            else:
                by_file[msg["file"]].append(msg)

        output_data: dict[str, Any] = {"files": {}}

        # Add file-grouped messages
        for file_path in sorted(by_file.keys()):
            file_messages = []
            for msg in sorted(by_file[file_path], key=lambda m: m["line_number"] or 0):
                file_msg: dict[str, Any] = {
                    "level": msg["level"].name,
                    "rule": msg["rule"],
                    "message": msg["message"],
                }
                if msg["line_number"]:
                    file_msg["line"] = msg["line_number"]
                file_messages.append(file_msg)
            output_data["files"][file_path] = file_messages

        # Add unknown messages
        if unknown_messages:
            unknown_file_messages = []
            for msg in unknown_messages:
                unknown_file_messages.append(
                    {
                        "level": msg["level"].name,
                        "rule": msg["rule"],
                        "message": msg["message"],
                    }
                )
            output_data["files"]["<unknown>"] = unknown_file_messages

        # Convert to YAML
        try:
            return yaml.dump(output_data, default_flow_style=False, sort_keys=False)
        except ImportError:
            raise RuntimeError("PyYAML is not installed, cannot format logs as YAML")

    def get_format(self) -> LogFormat:
        """Return YAML format"""
        return LogFormat.YAML
