import re
from pathlib import Path

from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class CodeSnippetValidator:
    """Validator for detecting and checking code snippets in markdown files"""

    def __init__(self, logger: Logger, max_lines: int = 3):
        self.logger = logger
        self.max_lines = max_lines

    def validate_code_snippets(self, file_path: Path, base_directory: Path, content: str) -> tuple[int, int]:
        """
        Validate code snippets in a markdown file
        Returns tuple of (warning_count, error_count)
        """
        # Find all code blocks using regex
        # Matches ```language\ncode\n``` or ```\ncode\n```
        code_block_pattern = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)
        matches = list(code_block_pattern.finditer(content))
        warnings = 0

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
                    file_path.relative_to(base_directory),
                    line_number,
                    match.group(0).partition("\n")[0],  # First line of the code block for context
                )
                warnings += 1

        return warnings, 0
