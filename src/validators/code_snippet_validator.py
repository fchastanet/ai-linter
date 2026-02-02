import re
from pathlib import Path

from lib.log import Logger, LogLevel


class CodeSnippetValidator:
    """Validator for detecting and checking code snippets in markdown files"""

    def __init__(self, logger: Logger, max_lines: int = 3):
        self.logger = logger
        self.max_lines = max_lines

    def validate_code_snippets(self, file_path: str | Path) -> tuple[int, int]:
        """
        Validate code snippets in a markdown file
        Returns tuple of (warning_count, error_count)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            self.logger.logRule(
                LogLevel.ERROR,
                "file-not-found",
                f"File not found: {file_path}",
                file_path,
            )
            return 0, 1

        try:
            content = file_path.read_text()
        except Exception as e:
            self.logger.logRule(
                LogLevel.ERROR,
                "file-read-error",
                f"Failed to read file: {e}",
                file_path,
            )
            return 0, 1

        warnings = 0
        errors = 0

        # Find all code blocks using regex
        # Matches ```language\ncode\n``` or ```\ncode\n```
        code_block_pattern = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)
        matches = list(code_block_pattern.finditer(content))

        if not matches:
            # No code blocks found - this is fine
            return 0, 0

        for match in matches:
            code_content = match.group(1)
            # Count lines in the code block
            lines = code_content.split("\n")
            line_count = len([line for line in lines if line.strip()])  # Count non-empty lines

            if line_count > self.max_lines:
                # Calculate line number in the file where the code block starts
                start_pos = match.start()
                line_number = content[:start_pos].count("\n") + 1

                self.logger.logRule(
                    LogLevel.WARNING,
                    "code-snippet-too-large",
                    f"Code snippet at line {line_number} has {line_count} lines (max: {self.max_lines}). "
                    f"Consider externalizing this code block to an external file to limit AI context size.",
                    file_path,
                    line_number,
                    match.group(0).partition("\n")[0],  # First line of the code block for context
                )
                warnings += 1

        return warnings, errors

    def validate_all_markdown_files(
        self, directory: str | Path, ignore_dirs: list[str] | None = None
    ) -> tuple[int, int]:
        """
        Validate code snippets in all markdown files within a directory
        Returns tuple of (warning_count, error_count)
        """
        directory = Path(directory)
        if ignore_dirs is None:
            ignore_dirs = []

        total_warnings = 0
        total_errors = 0

        # Find all .md files recursively
        for md_file in directory.rglob("*.md"):
            # Skip ignored directories
            if any(ignored in md_file.parts for ignored in ignore_dirs):
                continue

            warnings, errors = self.validate_code_snippets(md_file)
            total_warnings += warnings
            total_errors += errors

        return total_warnings, total_errors
