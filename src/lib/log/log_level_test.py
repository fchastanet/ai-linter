import logging

from lib.log.log_level import LogLevel


class TestLogLevel:
    """Test LogLevel enum functionality"""

    def test_enum_values(self) -> None:
        """Test that LogLevel enum has correct values"""
        assert LogLevel.ERROR.value == 0
        assert LogLevel.WARNING.value == 1
        assert LogLevel.ADVICE.value == 2
        assert LogLevel.INFO.value == 3
        assert LogLevel.DEBUG.value == 4

    def test_from_string_exact_match(self) -> None:
        """Test from_string with exact matches"""
        assert LogLevel.from_string("ERROR") == LogLevel.ERROR
        assert LogLevel.from_string("WARNING") == LogLevel.WARNING
        assert LogLevel.from_string("ADVICE") == LogLevel.ADVICE
        assert LogLevel.from_string("INFO") == LogLevel.INFO
        assert LogLevel.from_string("DEBUG") == LogLevel.DEBUG

    def test_from_string_case_insensitive(self) -> None:
        """Test from_string is case-insensitive"""
        assert LogLevel.from_string("error") == LogLevel.ERROR
        assert LogLevel.from_string("Warning") == LogLevel.WARNING
        assert LogLevel.from_string("advice") == LogLevel.ADVICE
        assert LogLevel.from_string("InFo") == LogLevel.INFO
        assert LogLevel.from_string("DeBuG") == LogLevel.DEBUG

    def test_from_string_synonyms(self) -> None:
        """Test from_string with synonyms"""
        assert LogLevel.from_string("ERR") == LogLevel.ERROR
        assert LogLevel.from_string("WARN") == LogLevel.WARNING
        assert LogLevel.from_string("ADV") == LogLevel.ADVICE
        assert LogLevel.from_string("INFORMATION") == LogLevel.INFO
        assert LogLevel.from_string("DBG") == LogLevel.DEBUG

    def test_from_string_invalid(self) -> None:
        """Test from_string with invalid values defaults to INFO"""
        assert LogLevel.from_string("INVALID") == LogLevel.INFO
        assert LogLevel.from_string("") == LogLevel.INFO

    def test_from_string_none(self) -> None:
        """Test from_string with None defaults to INFO"""
        assert LogLevel.from_string(None) == LogLevel.INFO  # type: ignore[arg-type]

    def test_from_string_with_loglevel(self) -> None:
        """Test from_string with LogLevel enum returns same value"""
        assert LogLevel.from_string(LogLevel.ERROR) == LogLevel.ERROR  # type: ignore[arg-type]
        assert LogLevel.from_string(LogLevel.ADVICE) == LogLevel.ADVICE  # type: ignore[arg-type]

    def test_to_python_level(self) -> None:
        """Test conversion to Python logging levels"""
        assert LogLevel.ERROR.to_python_level() == logging.ERROR
        assert LogLevel.WARNING.to_python_level() == logging.WARNING
        assert LogLevel.ADVICE.to_python_level() == logging.INFO
        assert LogLevel.INFO.to_python_level() == logging.INFO
        assert LogLevel.DEBUG.to_python_level() == logging.DEBUG

    def test_from_python_level(self) -> None:
        """Test conversion from Python logging levels"""
        assert LogLevel.from_python_level(logging.ERROR) == LogLevel.ERROR
        assert LogLevel.from_python_level(logging.WARNING) == LogLevel.WARNING
        assert LogLevel.from_python_level(logging.INFO) == LogLevel.INFO
        assert LogLevel.from_python_level(logging.DEBUG) == LogLevel.DEBUG
        # Unknown level defaults to INFO
        assert LogLevel.from_python_level(999) == LogLevel.INFO

    def test_get_level_color(self) -> None:
        """Test that each level has a color code"""
        from lib.log.log_colors import BLUE, CYAN, GRAY, RED, YELLOW

        assert LogLevel.ERROR.get_level_color() == RED
        assert LogLevel.WARNING.get_level_color() == YELLOW
        assert LogLevel.ADVICE.get_level_color() == CYAN
        assert LogLevel.INFO.get_level_color() == BLUE
        assert LogLevel.DEBUG.get_level_color() == GRAY

    def test_str_representation(self) -> None:
        """Test string representation of LogLevel"""
        assert str(LogLevel.ERROR) == "ERROR"
        assert str(LogLevel.WARNING) == "WARN"
        assert str(LogLevel.ADVICE) == "ADVICE"
        assert str(LogLevel.INFO) == "INFO"
        assert str(LogLevel.DEBUG) == "DEBUG"

    def test_is_valid_string(self) -> None:
        """Test is_valid_string method"""
        # Valid log levels
        assert LogLevel.is_valid_string("ERROR") is True
        assert LogLevel.is_valid_string("WARNING") is True
        assert LogLevel.is_valid_string("ADVICE") is True
        assert LogLevel.is_valid_string("INFO") is True
        assert LogLevel.is_valid_string("DEBUG") is True

        # Case insensitive
        assert LogLevel.is_valid_string("error") is True
        assert LogLevel.is_valid_string("Warning") is True

        # Valid synonyms
        assert LogLevel.is_valid_string("ERR") is True
        assert LogLevel.is_valid_string("WARN") is True
        assert LogLevel.is_valid_string("ADV") is True
        assert LogLevel.is_valid_string("INFORMATION") is True
        assert LogLevel.is_valid_string("INFOR") is True
        assert LogLevel.is_valid_string("DBG") is True

        # Invalid values
        assert LogLevel.is_valid_string("INVALID") is False
        assert LogLevel.is_valid_string("UNKNOWN") is False
        assert LogLevel.is_valid_string("") is False
        assert LogLevel.is_valid_string(None) is False  # type: ignore[arg-type]
