"""Unit tests for Logger report functionality"""

from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class TestLoggerReport:
    """Test Logger report entry functionality"""

    def test_log_report_entry_valid(self) -> None:
        """Test logging a valid report entry"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)

        logger.logReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Agent",
            tokens=100,
            max_tokens=5000,
            lines=10,
            max_lines=500,
            warning_threshold=0.8,
        )

        entries = logger.get_report_entries()
        assert len(entries) == 1
        assert entries[0].file_type == "Agent"
        assert entries[0].tokens == 100
        assert entries[0].lines == 10
        assert entries[0].status == "✅ Valid"

    def test_log_report_entry_warning_token(self) -> None:
        """Test logging a report entry with token warning"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)

        logger.logReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Prompt",
            tokens=4500,  # 90% of 5000
            max_tokens=5000,
            lines=100,
            max_lines=500,
            warning_threshold=0.8,
        )

        entries = logger.get_report_entries()
        assert len(entries) == 1
        assert "⚠️" in entries[0].status
        assert "token limit" in entries[0].status

    def test_log_report_entry_warning_line(self) -> None:
        """Test logging a report entry with line warning"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)

        logger.logReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Prompt",
            tokens=100,
            max_tokens=5000,
            lines=450,  # 90% of 500
            max_lines=500,
            warning_threshold=0.8,
        )

        entries = logger.get_report_entries()
        assert len(entries) == 1
        assert "⚠️" in entries[0].status
        assert "line limit" in entries[0].status

    def test_log_report_entry_error_token(self) -> None:
        """Test logging a report entry with token error"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)

        logger.logReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Agent",
            tokens=6000,
            max_tokens=5000,
            lines=100,
            max_lines=500,
            warning_threshold=0.8,
        )

        entries = logger.get_report_entries()
        assert len(entries) == 1
        assert "❌" in entries[0].status
        assert "token limit" in entries[0].status

    def test_log_report_entry_error_line(self) -> None:
        """Test logging a report entry with line error"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)

        logger.logReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Agent",
            tokens=100,
            max_tokens=5000,
            lines=600,
            max_lines=500,
            warning_threshold=0.8,
        )

        entries = logger.get_report_entries()
        assert len(entries) == 1
        assert "❌" in entries[0].status
        assert "line limit" in entries[0].status

    def test_log_report_entry_error_both(self) -> None:
        """Test logging a report entry with both errors"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)

        logger.logReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Agent",
            tokens=6000,
            max_tokens=5000,
            lines=600,
            max_lines=500,
            warning_threshold=0.8,
        )

        entries = logger.get_report_entries()
        assert len(entries) == 1
        assert "❌" in entries[0].status
        assert "token limit" in entries[0].status
        assert "line limit" in entries[0].status

    def test_log_multiple_report_entries(self) -> None:
        """Test logging multiple report entries"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)

        logger.logReportEntry("file1.md", 42, "Agent", 100, 5000, 10, 500, 0.8)
        logger.logReportEntry("file2.md", 42, "Prompt", 4500, 5000, 450, 500, 0.8)
        logger.logReportEntry("file3.md", 42, "Skill", 6000, 5000, 600, 500, 0.8)

        entries = logger.get_report_entries()
        assert len(entries) == 3
