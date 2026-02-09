"""Unit tests for LogfmtFormatter"""

import os

import pytest

from lib.log.log_format import LogFormat
from lib.log.log_formatters.logfmt_formatter import LogfmtFormatter
from lib.log.log_formatters.rule_message import RuleMessage
from lib.log.log_level import LogLevel


class TestLogfmtFormatter:
    """Tests for LogfmtFormatter"""

    @pytest.fixture
    def formatter(self) -> LogfmtFormatter:
        """Create a formatter instance"""
        return LogfmtFormatter()

    def test_get_format(self, formatter: LogfmtFormatter) -> None:
        """Test that formatter returns correct format"""
        assert formatter.get_format() == LogFormat.LOGFMT

    def test_format_no_messages(self, formatter: LogfmtFormatter) -> None:
        """Test formatting with no messages returns empty string"""
        result = formatter.format([], [], os.times())
        # Should still contain summary output
        assert 'rule="summary" path="<report>"' in result

    def test_format_single_file_single_error(self, formatter: LogfmtFormatter) -> None:
        """Test that logfmt formatter returns correctly formatted single error"""
        messages = [
            RuleMessage(
                level=LogLevel.ERROR,
                rule="test-rule",
                message="Test message",
                file="test.py",
                line_number=42,
            )
        ]
        result = formatter.format([], messages, os.times())
        # Check that error message is present
        assert 'rule="test-rule" path="test.py" line="42" message="Test message"' in result
        # Check for summary output
        assert 'rule="summary" path="<report>"' in result

    def test_format_multiple_errors_same_file(self, formatter: LogfmtFormatter) -> None:
        """Test formatting multiple errors in the same file"""
        messages = [
            RuleMessage(
                level=LogLevel.ERROR,
                rule="error1",
                message="First error",
                file="test.py",
                line_number=10,
            ),
            RuleMessage(
                level=LogLevel.WARNING,
                rule="warning1",
                message="First warning",
                file="test.py",
                line_number=5,
            ),
        ]
        result = formatter.format([], messages, os.times())
        # Check that both error and warning messages are present in the output
        assert 'rule="error1" path="test.py" line="10" message="First error"' in result
        assert 'rule="warning1" path="test.py" line="5" message="First warning"' in result
        # Check for summary output
        assert 'rule="summary" path="<report>"' in result

    def test_format_empty_messages(self, formatter: LogfmtFormatter) -> None:
        """Test formatting empty message list"""
        result = formatter.format([], [], os.times())
        # Should still contain summary output
        assert 'rule="summary" path="<report>"' in result
