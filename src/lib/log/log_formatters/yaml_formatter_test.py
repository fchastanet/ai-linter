"""Unit tests for YamlFormatter"""

import pytest
import yaml as pyyaml

from lib.log.log_format import LogFormat
from lib.log.log_formatters.rule_message import RuleMessage
from lib.log.log_formatters.yaml_formatter import YamlFormatter
from lib.log.log_level import LogLevel


class TestYamlFormatter:
    """Tests for YamlFormatter"""

    @pytest.fixture
    def formatter(self) -> YamlFormatter:
        """Create a formatter instance"""
        return YamlFormatter()

    def test_get_format(self, formatter: YamlFormatter) -> None:
        """Test that formatter returns correct format"""
        assert formatter.get_format() == LogFormat.YAML

    def test_format_single_error(self, formatter: YamlFormatter) -> None:
        """Test formatting a single error"""
        messages = [
            RuleMessage(
                level=LogLevel.ERROR,
                rule="test-error",
                message="Test error",
                file="test.py",
                line_number=42,
                otherParam="param1",
            )
        ]
        result = formatter.format(messages)
        data = pyyaml.safe_load(result)
        assert "files" in data
        assert "test.py" in data["files"]
        assert len(data["files"]["test.py"]) == 1
        assert data["files"]["test.py"][0]["rule"] == "test-error"
        assert data["files"]["test.py"][0]["level"] == "ERROR"
        assert data["files"]["test.py"][0]["line"] == 42

    def test_format_multiple_errors_same_file(self, formatter: YamlFormatter) -> None:
        """Test formatting multiple errors in same file"""
        messages = [
            RuleMessage(
                level=LogLevel.ERROR,
                rule="error1",
                message="First error",
                file="test.py",
                line_number=10,
                otherParam="param1",
            ),
            RuleMessage(
                level=LogLevel.WARNING,
                rule="warning1",
                message="First warning",
                file="test.py",
                line_number=5,
                otherParam="param2",
            ),
        ]
        result = formatter.format(messages)
        data = pyyaml.safe_load(result)
        assert len(data["files"]["test.py"]) == 2

    def test_format_errors_multiple_files(self, formatter: YamlFormatter) -> None:
        """Test formatting errors across multiple files"""
        messages = [
            RuleMessage(
                level=LogLevel.ERROR,
                rule="error1",
                message="Error in file1",
                file="file1.py",
                line_number=10,
                otherParam="param1",
            ),
            RuleMessage(
                level=LogLevel.ERROR,
                rule="error2",
                message="Error in file2",
                file="file2.py",
                line_number=20,
                otherParam="param1",
            ),
        ]
        result = formatter.format(messages)
        data = pyyaml.safe_load(result)
        assert "file1.py" in data["files"]
        assert "file2.py" in data["files"]

    def test_format_unknown_messages(self, formatter: YamlFormatter) -> None:
        """Test formatting messages with unknown file"""
        messages = [
            RuleMessage(
                level=LogLevel.INFO,
                rule="config-set",
                message="Config loaded",
                file="<unknown>",
                line_number=None,
                otherParam="param1",
            )
        ]
        result = formatter.format(messages)
        data = pyyaml.safe_load(result)
        assert "<unknown>" in data["files"]
        assert data["files"]["<unknown>"][0]["rule"] == "config-set"

    def test_format_message_without_line_number(self, formatter: YamlFormatter) -> None:
        """Test that line number is not included when None"""
        messages = [
            RuleMessage(
                level=LogLevel.ERROR,
                rule="test-error",
                message="Test error",
                file="test.py",
                line_number=None,
                otherParam="param1",
            )
        ]
        result = formatter.format(messages)
        data = pyyaml.safe_load(result)
        assert "line" not in data["files"]["test.py"][0]

    def test_format_empty_messages(self, formatter: YamlFormatter) -> None:
        """Test formatting empty message list"""
        result = formatter.format([])
        data = pyyaml.safe_load(result)
        assert data["files"] == {}
