"""Unit tests for LogfmtFormatter"""

import pytest

from lib.log import LogLevel
from lib.log_format import LogFormat
from lib.log_formatters.logfmt_formatter import LogfmtFormatter
from lib.log_formatters.rule_message import RuleMessage


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
        result = formatter.format([])
        assert result == ""

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
        result = formatter.format(messages)
        assert result == (
            '\033[31mlevel="ERROR" rule="test-rule" path="test.py" line="42" ' 'message="Test message"\033[0m\n'
        )

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
        result = formatter.format(messages)
        expected_output = (
            '\033[31mlevel="ERROR" rule="error1" path="test.py" line="10" '
            'message="First error"\033[0m\n'
            '\033[33mlevel="WARNING" rule="warning1" path="test.py" line="5" '
            'message="First warning"\033[0m\n'
        )
        assert result == expected_output

    def test_format_empty_messages(self, formatter: LogfmtFormatter) -> None:
        """Test formatting empty message list"""
        result = formatter.format([])
        assert result == ""
