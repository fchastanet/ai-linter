from pathlib import Path

import pytest

from lib.ai.stats import AiStats
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from validators.content_length_validator import ContentLengthValidator


class TestContentLengthValidator:
    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def ai_stats(self, logger: Logger) -> AiStats:
        """Create AI stats"""
        return AiStats(logger)

    @pytest.fixture
    def validator(self, logger: Logger, ai_stats: AiStats) -> ContentLengthValidator:
        """Create a ContentLengthValidator"""
        return ContentLengthValidator(logger, ai_stats)

    def test_content_within_limits(self, validator: ContentLengthValidator, tmp_path: Path) -> None:
        """Test content that is within line and token limits"""
        test_file = tmp_path / "test.md"
        content = "# Short content\n\nJust a few lines.\n"

        warnings, errors = validator.validate_content_length(
            content, test_file, 1, max_tokens=5000, max_lines=500, project_dir=tmp_path
        )
        assert errors == 0

    def test_content_exceeds_lines(self, validator: ContentLengthValidator, tmp_path: Path) -> None:
        """Test content that exceeds line limit"""
        test_file = tmp_path / "test.md"
        # Create content with more than 10 lines
        lines = "\n".join([f"Line {i}" for i in range(20)])

        warnings, errors = validator.validate_content_length(
            lines, test_file, 1, max_tokens=5000, max_lines=10, project_dir=tmp_path
        )
        assert errors == 1

    def test_content_with_empty_lines(self, validator: ContentLengthValidator, tmp_path: Path) -> None:
        """Test that empty lines are counted correctly"""
        test_file = tmp_path / "test.md"
        content = "Line 1\n\n\nLine 2"

        warnings, errors = validator.validate_content_length(
            content, test_file, 1, max_tokens=5000, max_lines=500, project_dir=tmp_path
        )
        assert errors == 0

    def test_content_single_line(self, validator: ContentLengthValidator, tmp_path: Path) -> None:
        """Test content with single line"""
        test_file = tmp_path / "test.md"
        content = "Single line content"

        warnings, errors = validator.validate_content_length(
            content, test_file, 1, max_tokens=5000, max_lines=500, project_dir=tmp_path
        )
        assert errors == 0

    def test_content_empty(self, validator: ContentLengthValidator, tmp_path: Path) -> None:
        """Test empty content"""
        test_file = tmp_path / "test.md"
        content = ""

        warnings, errors = validator.validate_content_length(
            content, test_file, 1, max_tokens=5000, max_lines=500, project_dir=tmp_path
        )
        assert errors == 0
