"""Unit tests for LogfmtFormatter"""

import pytest

from lib.log import LogLevel
from lib.log_format import LogFormat
from lib.log_formatters.logfmt_formatter import LogfmtFormatter


class TestLogfmtFormatter:
    """Tests for LogfmtFormatter"""

    @pytest.fixture
    def formatter(self) -> LogfmtFormatter:
        """Create a formatter instance"""
        return LogfmtFormatter()

    def test_get_format(self, formatter: LogfmtFormatter) -> None:
        """Test that formatter returns correct format"""
        assert formatter.get_format() == LogFormat.LOGFMT

    def test_format_returns_empty_string(self, formatter: LogfmtFormatter) -> None:
        """Test that logfmt formatter returns empty string (messages printed immediately)"""
        messages = [
            {
                "level": LogLevel.ERROR,
                "rule": "test-rule",
                "message": "Test message",
                "file": "test.py",
                "line_number": 42,
                "kwargs": {},
            }
        ]
        result = formatter.format(messages)
        assert result == ""

    def test_format_empty_messages(self, formatter: LogfmtFormatter) -> None:
        """Test formatting empty message list"""
        result = formatter.format([])
        assert result == ""
