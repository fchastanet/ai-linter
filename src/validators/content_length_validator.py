from pathlib import Path

from lib.ai.stats import AiStats
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class ContentLengthValidator:
    def __init__(self, logger: Logger, aiStats: AiStats):
        self.logger = logger
        self.aiStats = aiStats

    def validate_content_length(
        self, content: str, file: Path, line_number: int, max_tokens: int, max_lines: int, project_dir: Path
    ) -> tuple[int, int]:
        """Validate the length of the content"""
        nb_warnings = 0
        nb_errors = 0
        # Check content token count
        token_count = self.aiStats.compute_token_count_accurate(content)
        if token_count > max_tokens:
            self.logger.logRule(
                LogLevel.WARNING,
                "too-complex-content",
                f"Content is too complex ({token_count}/{max_tokens} tokens).",
                file=file.relative_to(project_dir),
                line_number=line_number,
            )
            nb_warnings += 1
        else:
            self.logger.logRule(
                LogLevel.INFO,
                "content-complexity",
                f"Content token count: {token_count}/{max_tokens} tokens.",
                file=file.relative_to(project_dir),
                line_number=line_number,
            )

        # Check content line count (max 500 lines per spec)
        line_count = content.count("\n") + 1
        if line_count > max_lines:
            self.logger.logRule(
                LogLevel.ERROR,
                "too-many-lines",
                f"Content has too many lines ({line_count}/{max_lines} lines).",
                file=file.relative_to(project_dir),
                line_number=line_number,
            )
            nb_errors += 1

        return nb_warnings, nb_errors
