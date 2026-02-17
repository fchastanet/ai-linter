import os
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from lib.arguments import Arguments
from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class TestArguments:
    """Test suite for Arguments class"""

    @pytest.fixture
    def logger(self) -> Logger:
        """Create a mock logger for testing"""
        mock = MagicMock(spec=Logger)
        return mock  # type: ignore[return-value]

    def test_arguments_creation(self) -> None:
        """Test Arguments object creation with valid parameters"""
        args = Arguments(
            skills=True,
            directories=["/path/to/dir"],
            config_file=None,
            log_level=LogLevel.INFO,
            log_format=LogFormat.FILE_DIGEST,
            max_warnings=10,
            ignore=None,
        )

        assert args.skills is True
        assert args.directories == ["/path/to/dir"]
        assert args.config_file is None
        assert args.log_level == LogLevel.INFO
        assert args.log_format == LogFormat.FILE_DIGEST
        assert args.max_warnings == 10
        assert args.ignore is None

    def test_arguments_with_multiple_directories(self) -> None:
        """Test Arguments with multiple directories"""
        dirs = ["/path/one", "/path/two", "/path/three"]
        args = Arguments(
            skills=False,
            directories=dirs,
            config_file="/path/to/config.yaml",
            log_level=LogLevel.DEBUG,
            log_format=LogFormat.YAML,
            max_warnings=5,
            ignore=[".git", "node_modules"],
        )

        assert args.directories == dirs
        assert len(args.directories) == 3
        assert args.ignore == [".git", "node_modules"]

    def test_arguments_with_none_values(self) -> None:
        """Test Arguments with None values"""
        args = Arguments(
            skills=False,
            directories=["/path"],
            config_file=None,
            log_level=None,
            log_format=None,
            max_warnings=None,
            ignore=None,
        )

        assert args.config_file is None
        assert args.log_level is None
        assert args.log_format is None
        assert args.max_warnings is None
        assert args.ignore is None

    @patch("sys.argv", ["ai-linter", "examples"])
    def test_parse_arguments_minimal(self, logger: Logger) -> None:
        """Test parsing minimal arguments"""
        with patch("sys.argv", ["ai-linter", "examples"]):
            args, return_code = Arguments.parse_arguments(logger, "1.0.0")

        assert return_code == 0
        assert args is not None
        assert args.skills is False
        assert args.directories == ["examples"]

    @patch("sys.argv", ["ai-linter", "--skills", "examples"])
    def test_parse_arguments_with_skills(self, logger: Logger) -> None:
        """Test parsing arguments with --skills flag"""
        with patch("sys.argv", ["ai-linter", "--skills", "examples"]):
            args, return_code = Arguments.parse_arguments(logger, "1.0.0")

        assert return_code == 0
        assert args.skills is True

    @patch("sys.argv", ["ai-linter", "--log-level", "DEBUG", "examples"])
    def test_parse_arguments_with_log_level(self, logger: Logger) -> None:
        """Test parsing arguments with log level"""
        with patch("sys.argv", ["ai-linter", "--log-level", "DEBUG", "examples"]):
            args, return_code = Arguments.parse_arguments(logger, "1.0.0")

        assert return_code == 0
        assert args.log_level == LogLevel.DEBUG

    @patch("sys.argv", ["ai-linter", "--max-warnings", "5", "examples"])
    def test_parse_arguments_with_max_warnings(self, logger: Logger) -> None:
        """Test parsing arguments with max warnings"""
        with patch("sys.argv", ["ai-linter", "--max-warnings", "5", "examples"]):
            args, return_code = Arguments.parse_arguments(logger, "1.0.0")

        assert return_code == 0
        assert args.max_warnings == 5

    @patch("sys.argv", ["ai-linter", "--log-format", "yaml", "examples"])
    def test_parse_arguments_with_log_format(self, logger: Logger) -> None:
        """Test parsing arguments with log format"""
        with patch("sys.argv", ["ai-linter", "--log-format", "yaml", "examples"]):
            args, return_code = Arguments.parse_arguments(logger, "1.0.0")

        assert return_code == 0
        assert args.log_format == LogFormat.YAML

    @patch("sys.argv", ["ai-linter", "/nonexistent"])
    def test_parse_arguments_invalid_directory(self, logger: Logger) -> None:
        """Test parsing with non-existent directory"""
        with patch("sys.argv", ["ai-linter", "/nonexistent"]):
            args, return_code = Arguments.parse_arguments(logger, "1.0.0")

        # Should return error code 1 for non-existent directory
        assert return_code == 1
        # Verify logger was called (type: ignore to avoid mypy issues with mocks)
        assert logger.log.called  # type: ignore[attr-defined]

    def test_parse_arguments_with_valid_config_file(self, logger: Logger) -> None:
        """Test parsing with valid config file"""
        with TemporaryDirectory() as tmpdir:
            # Create a dummy config file
            config_file = os.path.join(tmpdir, ".ai-linter-config.yaml")
            with open(config_file, "w") as f:
                f.write("log_level: INFO\n")

            main_dir = tmpdir
            with patch("sys.argv", ["ai-linter", "--config-file", config_file, main_dir]):
                args, return_code = Arguments.parse_arguments(logger, "1.0.0")

            assert return_code == 0
            assert args.config_file == config_file

    @patch("sys.argv", ["ai-linter", "--config-file", "/nonexistent.yaml", "examples"])
    def test_parse_arguments_invalid_config_file(self, logger: Logger) -> None:
        """Test parsing with non-existent config file"""
        with patch("sys.argv", ["ai-linter", "--config-file", "/nonexistent.yaml", "examples"]):
            args, return_code = Arguments.parse_arguments(logger, "1.0.0")

        # Should return error code 1 for non-existent config file
        assert return_code == 1
        # Verify logger was called (type: ignore to avoid mypy issues with mocks)
        assert logger.log.called  # type: ignore[attr-defined]

    @patch("sys.argv", ["ai-linter", "examples", "examples"])
    def test_parse_arguments_duplicate_directories(self, logger: Logger) -> None:
        """Test parsing with duplicate directories (should be deduplicated)"""
        with patch("sys.argv", ["ai-linter", "examples", "examples"]):
            args, return_code = Arguments.parse_arguments(logger, "1.0.0")

        assert return_code == 0
        # Directories should be deduplicated
        assert len(args.directories) == 1
        assert args.directories == ["examples"]

    @patch("sys.argv", ["ai-linter", "--skills", "--log-level", "DEBUG", "--max-warnings", "10", "examples"])
    def test_parse_arguments_combined(self, logger: Logger) -> None:
        """Test parsing with combined arguments"""
        with patch(
            "sys.argv",
            [
                "ai-linter",
                "--skills",
                "--log-level",
                "DEBUG",
                "--max-warnings",
                "10",
                "examples",
                "--ignore",
                ".git",
                "--ignore",
                "node_modules",
            ],
        ):
            args, return_code = Arguments.parse_arguments(logger, "1.0.0")

        assert return_code == 0
        assert args.skills is True
        assert args.log_level == LogLevel.DEBUG
        assert args.max_warnings == 10
        assert args.directories == ["examples"]
        assert args.ignore == [".git", "node_modules"]
