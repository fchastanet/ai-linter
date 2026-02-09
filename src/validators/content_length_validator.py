from pathlib import Path

from lib.ai.stats import AiStats
from lib.log.logger import Logger


class ContentLengthValidator:
    def __init__(self, logger: Logger, aiStats: AiStats):
        self.logger = logger
        self.aiStats = aiStats

    def validate_content_length(
        self,
        content: str,
        file: Path,
        line_number: int,
        max_tokens: int,
        max_lines: int,
        project_dir: Path,
        file_type: str = "Unknown",
        warning_threshold: float = 0.8,
    ) -> tuple[int, int]:
        """Validate the length of the content and log report entry"""
        # Check content token count
        token_count = self.aiStats.compute_token_count_accurate(content)

        # Check content line count (max 500 lines per spec)
        line_count = content.count("\n") + 1

        # Log report entry for the file
        return self.logger.logReportEntry(
            file_path=str(file.relative_to(project_dir)),
            file_type=file_type,
            tokens=token_count,
            max_tokens=max_tokens,
            lines=line_count,
            max_lines=max_lines,
            warning_threshold=warning_threshold,
            line_number=line_number,
        )
