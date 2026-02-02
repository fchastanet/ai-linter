"""Unit tests for FileDigestFormatter"""

import pytest

from lib.log import LogLevel
from lib.log_format import LogFormat
from lib.log_formatters.file_digest_formatter import FileDigestFormatter


class TestFileDigestFormatter:
    """Tests for FileDigestFormatter"""

    @pytest.fixture
    def formatter(self) -> FileDigestFormatter:
        """Create a formatter instance"""
        return FileDigestFormatter()

    def test_get_format(self, formatter: FileDigestFormatter) -> None:
        """Test that formatter returns correct format"""
        assert formatter.get_format() == LogFormat.FILE_DIGEST

    def test_format_single_file_single_error(self, formatter: FileDigestFormatter) -> None:
        """Test formatting a single error in a single file"""
        messages = [
            {
                "level": LogLevel.ERROR,
                "rule": "test-error",
                "message": "Test error",
                "file": "test.py",
                "line_number": 42,
                "kwargs": {},
            }
        ]
        result = formatter.format(messages)
        assert "test.py" in result
        assert "line 42" in result
        assert "test-error" in result
        assert "Test error" in result

    def test_format_multiple_errors_same_file(self, formatter: FileDigestFormatter) -> None:
        """Test formatting multiple errors in the same file"""
        messages = [
            {
                "level": LogLevel.ERROR,
                "rule": "error1",
                "message": "First error",
                "file": "test.py",
                "line_number": 10,
                "kwargs": {},
            },
            {
                "level": LogLevel.WARNING,
                "rule": "warning1",
                "message": "First warning",
                "file": "test.py",
                "line_number": 5,
                "kwargs": {},
            },
        ]
        result = formatter.format(messages)
        assert "test.py" in result
        assert "line 5" in result
        assert "line 10" in result
        assert "error1" in result
        assert "warning1" in result

    def test_format_errors_multiple_files(self, formatter: FileDigestFormatter) -> None:
        """Test formatting errors across multiple files"""
        messages = [
            {
                "level": LogLevel.ERROR,
                "rule": "error1",
                "message": "Error in file1",
                "file": "file1.py",
                "line_number": 10,
                "kwargs": {},
            },
            {
                "level": LogLevel.ERROR,
                "rule": "error2",
                "message": "Error in file2",
                "file": "file2.py",
                "line_number": 20,
                "kwargs": {},
            },
        ]
        result = formatter.format(messages)
        assert "file1.py" in result
        assert "file2.py" in result

    def test_format_unknown_file_messages(self, formatter: FileDigestFormatter) -> None:
        """Test formatting messages with unknown file"""
        messages = [
            {
                "level": LogLevel.INFO,
                "rule": "config-set",
                "message": "Config loaded",
                "file": "<unknown>",
                "line_number": None,
                "kwargs": {},
            }
        ]
        result = formatter.format(messages)
        assert "<unknown>" in result
        assert "config-set" in result

    def test_format_empty_messages(self, formatter: FileDigestFormatter) -> None:
        """Test formatting empty message list"""
        result = formatter.format([])
        assert result == ""

    def test_format_messages_sorted_by_line(self, formatter: FileDigestFormatter) -> None:
        """Test that messages are sorted by line number within each file"""
        messages = [
            {
                "level": LogLevel.ERROR,
                "rule": "error3",
                "message": "Line 30",
                "file": "test.py",
                "line_number": 30,
                "kwargs": {},
            },
            {
                "level": LogLevel.ERROR,
                "rule": "error1",
                "message": "Line 10",
                "file": "test.py",
                "line_number": 10,
                "kwargs": {},
            },
            {
                "level": LogLevel.ERROR,
                "rule": "error2",
                "message": "Line 20",
                "file": "test.py",
                "line_number": 20,
                "kwargs": {},
            },
        ]
        result = formatter.format(messages)
        line10_pos = result.find("Line 10")
        line20_pos = result.find("Line 20")
        line30_pos = result.find("Line 30")
        assert line10_pos < line20_pos < line30_pos
