import re
from pathlib import Path

import yaml

from lib.log import Logger, LogLevel


class Parser:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def set_logger(self, logger: Logger) -> "Parser":
        """Set the logger instance"""
        self.logger = logger
        return self

    def get_frontmatter_line_number(self, frontmatter_text: str, key: str) -> int:
        """Get the line number of a key in the frontmatter text"""
        lines = frontmatter_text.split("\n")
        keyStr = f"{key}:"
        for i, line in enumerate(lines, start=1):
            if line.startswith(keyStr):
                return i
        return 0

    def parse_content_and_frontmatter(
        self, path: str | Path, frontmatter_required: bool = False
    ) -> tuple[str | None, str]:
        """Parse the content and frontmatter of a markdown file"""
        markdown_path = Path(path)
        content = markdown_path.read_text()
        if not content.startswith("---"):
            self.logger.log(
                LogLevel.ERROR if frontmatter_required else LogLevel.DEBUG,
                "no-frontmatter",
                "No YAML frontmatter found",
                markdown_path,
            )
            return None, content
        # Extract frontmatter
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        if not frontmatter_match:
            self.logger.log(
                LogLevel.ERROR if frontmatter_required else LogLevel.DEBUG,
                "missing-frontmatter",
                "Missing or invalid frontmatter in markdown file",
                markdown_path,
            )
            return None, content
        frontmatter_text = frontmatter_match.group(1)
        skill_content = frontmatter_match.group(2)
        return frontmatter_text, skill_content

    def parse_frontmatter(self, frontmatter_text: str, path: str | Path) -> tuple[dict | None, int, int]:
        # Parse YAML frontmatter
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                self.logger.log(
                    LogLevel.ERROR,
                    "invalid-frontmatter-format",
                    "Frontmatter must be a YAML dictionary",
                    path,
                )
                return None, 1, 0
        except yaml.YAMLError as e:
            self.logger.log(
                LogLevel.ERROR,
                "invalid-yaml",
                f"Invalid YAML in frontmatter: {e}",
                path,
            )
            return None, 1, 0

        return frontmatter, 0, 0
