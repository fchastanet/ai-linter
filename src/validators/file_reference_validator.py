import re
from pathlib import Path
from typing import Sequence

from lib.log import Logger, LogLevel


class FileReferenceValidator:
    def __init__(self, logger: Logger):
        self.logger = logger

    def validate_content_file_references(
        self, base_dirs: Sequence[str | Path], file: Path, content: str, content_start_line_number: int
    ) -> tuple[int, int]:
        """Parse content to extract file links (if any)"""
        file_links: dict[str, bool] = {}
        file_error_count = 0
        file_warning_count = 0
        for m in re.finditer(r"(?<!`)`(?P<link>[^`\n]+)`(?!`)", content):
            link = m.group("link")
            self.logger.log(
                LogLevel.DEBUG,
                "file-link-found",
                f"Found file link: {link}",
                file,
            )
            # check if it seems like a file path (i.e., contains at least one /)
            # Regex: at least one /, and no * or ?
            # @see https://regex101.com/r/gRA5Sy/1
            if re.search(r"^(?=[^*?]*\/)[^*?\\<>$|:\"']+$", link) and file_links.get(link) is None:
                self.logger.log(
                    LogLevel.DEBUG,
                    "validating-file-link",
                    f"Validating file link: {link}",
                    file,
                )
                file_links[link] = True
                if not self._validate_file_link(base_dirs, file, content, m, link, content_start_line_number):
                    file_error_count += 1

        return file_warning_count, file_error_count

    def validate_content_length(
        self, content: str, file: str | Path, line_number: int, max_tokens: int, max_lines: int
    ) -> tuple[int, int]:
        """Validate the length of the content"""
        nb_warnings = 0
        nb_errors = 0
        # Check content token count
        token_count = self._compute_token_count_accurate(content)
        if token_count > max_tokens:
            self.logger.log(
                LogLevel.WARNING,
                "too-complex-content",
                f"Content is too complex ({token_count}/{max_tokens} tokens).",
                file,
                line_number=line_number,
            )
            nb_warnings += 1
        else:
            self.logger.log(
                LogLevel.INFO,
                "content-complexity",
                f"Content token count: {token_count}/{max_tokens} tokens.",
                file,
                line_number=line_number,
            )

        # Check content line count (max 500 lines per spec)
        line_count = content.count("\n") + 1
        if line_count > max_lines:
            self.logger.log(
                LogLevel.ERROR,
                "too-many-lines",
                f"Content has too many lines ({line_count}/{max_lines} lines).",
                file,
                line_number=line_number,
            )
            nb_errors += 1

        return nb_warnings, nb_errors

    def _validate_file_link(
        self,
        base_dirs: Sequence[str | Path],
        file: str | Path,
        content: str,
        match: re.Match[str],
        link: str,
        content_start_line_number: int,
    ) -> bool:
        """Validate that a file link exists relative to base directories"""
        # Determine line number of the link
        start_pos = match.start()
        line_number = content.count("\n", 0, start_pos) + 1 + content_start_line_number
        # Check if the file exists relative to any of the base directories
        for base_dir in base_dirs:
            file_path = Path(base_dir) / link
            if file_path.exists():
                return True

        self.logger.log(
            LogLevel.ERROR,
            "file-link-not-found",
            f"File link '{link}' not found in any of the base directories: {base_dirs}",
            file,
            line_number=line_number,
        )
        return False

    def _compute_token_count_accurate(self, text: str) -> int:
        """Compute token count for a given text using tiktoken if available"""
        try:
            import tiktoken  # pyright: ignore[reportMissingImports]

            encoder = tiktoken.get_encoding("cl100k_base")
            tokens = encoder.encode(text)
            return len(tokens)
        except ImportError:
            self.logger.log(
                LogLevel.WARNING,
                "tiktoken-not-found",
                "tiktoken not found, using naive token count approximation.",
            )
            # Fallback to naive approximation if tiktoken is not available
            return len(text) // 4
