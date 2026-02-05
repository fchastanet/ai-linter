"""Unit tests for Logger class"""

from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class TestLogger:
    """Tests for Logger class"""

    def test_logger_initialization_default(self) -> None:
        """Test logger initialization with defaults"""
        logger = Logger()
        assert logger.level == LogLevel.INFO
        assert logger.log_format == LogFormat.FILE_DIGEST
        assert logger.messages == []

    def test_logger_initialization_with_params(self) -> None:
        """Test logger initialization with specific level and format"""
        logger = Logger(LogLevel.DEBUG, LogFormat.YAML)
        assert logger.level == LogLevel.DEBUG
        assert logger.log_format == LogFormat.YAML

    def test_set_level(self) -> None:
        """Test changing log level"""
        logger = Logger(LogLevel.INFO)
        assert logger.level == LogLevel.INFO
        logger.set_level(LogLevel.DEBUG)
        assert logger.level == LogLevel.DEBUG

    def test_set_format(self) -> None:
        """Test changing log format"""
        logger = Logger(format=LogFormat.FILE_DIGEST)
        assert logger.log_format == LogFormat.FILE_DIGEST
        logger.set_format(LogFormat.YAML)
        assert logger.log_format == LogFormat.YAML

    def test_log_filtering_by_level(self) -> None:
        """Test that messages below log level are filtered"""
        logger = Logger(LogLevel.ERROR)
        logger.logRule(LogLevel.INFO, "info-rule", "Info message", "test.py", 10)
        logger.logRule(LogLevel.ERROR, "error-rule", "Error message", "test.py", 20)
        # Should only have the ERROR message
        assert len(logger.messages) == 1
        assert logger.messages[0].rule == "error-rule"

    def test_log_buffering_for_file_digest(self) -> None:
        """Test message buffering for file-digest format"""
        logger = Logger(format=LogFormat.FILE_DIGEST)
        logger.logRule(LogLevel.ERROR, "test-rule", "Test message", "test.py", 42)
        assert len(logger.messages) == 1
        assert logger.messages[0].file == "test.py"

    def test_flush_clears_messages(self) -> None:
        """Test that flush clears the message buffer"""
        logger = Logger(format=LogFormat.FILE_DIGEST)
        logger.logRule(LogLevel.ERROR, "test-rule", "Test message", "test.py", 42)
        assert len(logger.messages) == 1
        logger.flush()
        assert len(logger.messages) == 0

    def test_try_relative_path_with_none(self) -> None:
        """Test relative path conversion with None"""
        logger = Logger()
        result = logger.try_relative_path(None)
        assert str(result) == "<unknown>"

    def test_try_relative_path_with_absolute_path(self) -> None:
        """Test relative path conversion with absolute path"""
        from pathlib import Path

        logger = Logger()
        # Use a path that should exist
        cwd = Path.cwd()
        result = logger.try_relative_path(cwd / "test.py")
        assert str(result) == "test.py"

    def test_buffer_message_structure(self) -> None:
        """Test that buffered messages have correct structure"""
        logger = Logger(format=LogFormat.FILE_DIGEST)
        logger.logRule(LogLevel.WARNING, "test-rule", "Test message", "test.py", 42)
        assert len(logger.messages) == 1
        msg = logger.messages[0]
        assert msg.level == LogLevel.WARNING
        assert msg.rule == "test-rule"
        assert msg.message == "Test message"
        assert msg.line_number == 42

    def test_log_without_line_number(self) -> None:
        """Test logging without line number"""
        logger = Logger(format=LogFormat.FILE_DIGEST)
        logger.logRule(LogLevel.INFO, "test-rule", "Test message", "test.py")
        assert logger.messages[0].line_number is None

    def test_log_with_unknown_file(self) -> None:
        """Test logging with unknown file"""
        logger = Logger(format=LogFormat.FILE_DIGEST)
        logger.logRule(LogLevel.INFO, "test-rule", "Test message")
        assert logger.messages[0].file == "<unknown>"

    def test_log_general_message(self) -> None:
        """Test logging a general operational message"""
        logger = Logger()
        # General messages should not be buffered
        logger.log(LogLevel.INFO, "This is an operational message")
        # Messages should be empty for operational logs
        assert len(logger.messages) == 0

    def test_logRule_with_file_and_line(self) -> None:
        """Test logRule with file and line information"""
        logger = Logger(format=LogFormat.FILE_DIGEST)
        logger.logRule(LogLevel.ERROR, "invalid-format", "Invalid format detected", "test.md", 10)
        assert len(logger.messages) == 1
        assert logger.messages[0].rule == "invalid-format"
        assert logger.messages[0].file == "test.md"
        assert logger.messages[0].line_number == 10
