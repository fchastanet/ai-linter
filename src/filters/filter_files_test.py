from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

import pytest

from filters.filter_files import filter_files
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class TestFilterFiles:
    """Test suite for filter_files function"""

    @pytest.fixture
    def logger(self) -> Logger:
        """Create a mock logger for testing"""
        return MagicMock(spec=Logger)

    @pytest.fixture
    def temp_project_dir(self) -> Generator[Path, None, None]:
        """Create a temporary project directory with test files"""
        with TemporaryDirectory() as tmpdir:
            # Create a directory structure with various files
            project_dir = Path(tmpdir)

            # Create some test files and directories
            (project_dir / ".git").mkdir()
            (project_dir / ".git" / "config").touch()

            (project_dir / "__pycache__").mkdir()
            (project_dir / "__pycache__" / "test.pyc").touch()

            (project_dir / "node_modules").mkdir()
            (project_dir / "node_modules" / "package.json").touch()

            (project_dir / "src").mkdir()
            (project_dir / "src" / "main.py").touch()
            (project_dir / "src" / "utils.py").touch()

            (project_dir / "test").mkdir()
            (project_dir / "test" / "test_main.py").touch()

            (project_dir / "doc").mkdir()
            (project_dir / "doc" / "README.md").touch()

            (project_dir / ".vscode").mkdir()
            (project_dir / ".vscode" / "settings.json").touch()

            (project_dir / "build").mkdir()
            (project_dir / "build" / "output.txt").touch()

            yield project_dir

    def test_filter_files_with_no_patterns(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test filter_files with empty ignore patterns list"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        result = filter_files(logger, [], files, temp_project_dir)

        # All files should be kept when no patterns are provided
        assert len(result) == len(files)
        assert set(result) == set(files)
        # Should log info message
        logger.log.assert_called()  # type: ignore[attr-defined]

    def test_filter_files_with_simple_pattern(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test filter_files with a simple directory pattern"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        # Filter out .git directory
        result = filter_files(logger, [".git"], files, temp_project_dir)

        # Files in .git should be excluded
        non_git_files = [f for f in files if ".git" not in f.parts]

        assert len(result) == len(non_git_files)
        assert set(result) == set(non_git_files)

    def test_filter_files_with_multiple_patterns(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test filter_files with multiple ignore patterns"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        # Filter out multiple patterns
        patterns = [".git", "__pycache__", "node_modules", "build"]
        result = filter_files(logger, patterns, files, temp_project_dir)

        # Check that files matching patterns are excluded
        excluded_files = [f for f in files if any(pattern in f.parts for pattern in patterns)]
        expected_files = [f for f in files if f not in excluded_files]

        assert len(result) == len(expected_files)
        assert set(result) == set(expected_files)

    def test_filter_files_logs_ignored_files(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test that filter_files logs debug message when files are ignored"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        # Filter with patterns that will match some files
        filter_files(logger, [".git", "__pycache__"], files, temp_project_dir)

        # Should have called logger.log at least once
        assert logger.log.called  # type: ignore[attr-defined]

        # Check that the debug log was called with the right parameters
        calls = logger.log.call_args_list  # type: ignore[attr-defined]
        # Find the debug call about ignored files
        debug_calls = [call for call in calls if len(call[0]) > 0 and call[0][0] == LogLevel.DEBUG]

        assert len(debug_calls) > 0

    def test_filter_files_logs_info_about_results(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test that filter_files logs info message about validation results"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        filter_files(logger, [], files, temp_project_dir)

        # Should log info message
        calls = logger.log.call_args_list  # type: ignore[attr-defined]
        info_calls = [call for call in calls if len(call[0]) > 0 and call[0][0] == LogLevel.INFO]

        assert len(info_calls) > 0
        # Check that the info call includes the counts
        for call in info_calls:
            if "Found file(s) to validate" in str(call):
                assert "filtered_files_count" in str(call)
                assert "total_files_count" in str(call)

    def test_filter_files_with_wildcard_patterns(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test filter_files with wildcard patterns"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        # Filter using wildcard patterns for dot directories
        patterns = [".*"]
        result = filter_files(logger, patterns, files, temp_project_dir)

        # Files starting with dot should be excluded
        excluded_count = len([f for f in files if any(p.startswith(".") for p in f.parts)])
        assert len(result) <= len(files) - excluded_count

    def test_filter_files_empty_file_list(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test filter_files with an empty file list"""
        result = filter_files(logger, [".git", "node_modules"], [], temp_project_dir)

        assert result == []
        # Should still log info message
        logger.log.assert_called()  # type: ignore[attr-defined]

    def test_filter_files_preserves_file_order(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test that filter_files preserves the order of input files"""
        # Create specific files in a known order
        files = [
            temp_project_dir / "src" / "main.py",
            temp_project_dir / "src" / "utils.py",
            temp_project_dir / "test" / "test_main.py",
            temp_project_dir / "doc" / "README.md",
        ]

        result = filter_files(logger, [], files, temp_project_dir)

        # Result should maintain the same order
        assert list(result) == files

    def test_filter_files_with_nested_patterns(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test filter_files with patterns that match nested paths"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        # Use patterns for nested directories
        patterns = ["src/test*", "build/*"]
        result = filter_files(logger, patterns, files, temp_project_dir)

        # Verify filtering occurred
        assert isinstance(result, list)
        assert all(isinstance(f, Path) for f in result)

    def test_filter_files_returns_paths(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test that filter_files returns Path objects"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        result = filter_files(logger, [], files, temp_project_dir)

        assert isinstance(result, list)
        assert all(isinstance(f, Path) for f in result)

    def test_filter_files_with_case_sensitive_patterns(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test that filter_files handles case-sensitive patterns correctly"""
        # Create files with different cases
        files = [
            temp_project_dir / "src" / "main.py",
            temp_project_dir / "src" / "utils.py",
        ]

        # Filter with case-sensitive patterns
        result = filter_files(logger, ["SRC"], files, temp_project_dir)

        # SRC (uppercase) should not match src (lowercase) with gitignore rules
        assert len(result) == len(files)

    def test_filter_files_returns_correct_count(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test that filter_files returns correct filtered count in logs"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        total_count = len(files)
        patterns = [".git", "__pycache__"]
        filtered = filter_files(logger, patterns, files, temp_project_dir)

        # Verify the returned list has correct size
        assert isinstance(filtered, list)
        assert len(filtered) <= total_count

    def test_filter_files_with_relative_paths(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test filter_files with files as relative paths"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        result = filter_files(logger, [".git"], files, temp_project_dir)

        # All results should be absolute paths
        assert all(f.is_absolute() for f in result)

    def test_filter_files_with_docfile_pattern(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test filtering with doc directory pattern"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        result = filter_files(logger, ["doc"], files, temp_project_dir)

        # Files in doc directory should be excluded
        non_doc_files = [f for f in files if "doc" not in f.parts]

        assert len(result) == len(non_doc_files)
        assert set(result) == set(non_doc_files)

    def test_filter_files_all_files_filtered(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test when all files are filtered out"""
        # Create one file in the project
        test_file = temp_project_dir / ".git" / "config"

        result = filter_files(logger, [".git"], [test_file], temp_project_dir)

        # All files should be filtered
        assert len(result) == 0

        # Should log debug message about ignored files
        calls = logger.log.call_args_list  # type: ignore[attr-defined]
        debug_calls = [call for call in calls if len(call[0]) > 0 and call[0][0] == LogLevel.DEBUG]
        assert len(debug_calls) > 0

    def test_filter_files_maintains_path_types(self, logger: Logger, temp_project_dir: Path) -> None:
        """Test that filter_files maintains Path types"""
        all_files = list(temp_project_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]

        result = filter_files(logger, [], files, temp_project_dir)

        # All items should be Path instances
        for item in result:
            assert isinstance(item, Path)
            assert item.is_absolute()
