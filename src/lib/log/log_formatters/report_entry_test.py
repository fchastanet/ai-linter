"""Unit tests for ReportEntry class"""

from lib.log.log_formatters.report_entry import ReportEntry


class TestReportEntry:
    """Test ReportEntry data class"""

    def test_report_entry_creation(self) -> None:
        """Test creating a report entry"""
        entry = ReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Agent",
            tokens=100,
            max_tokens=5000,
            lines=10,
            max_lines=500,
            status="✅ Valid",
        )

        assert entry.file_path == "test.md"
        assert entry.file_type == "Agent"
        assert entry.tokens == 100
        assert entry.max_tokens == 5000
        assert entry.lines == 10
        assert entry.max_lines == 500
        assert entry.status == "✅ Valid"

    def test_get_severity_valid(self) -> None:
        """Test severity for valid status"""
        entry = ReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Agent",
            tokens=100,
            max_tokens=5000,
            lines=10,
            max_lines=500,
            status="✅ Valid",
        )

        assert entry.get_severity() == 0

    def test_get_severity_warning(self) -> None:
        """Test severity for warning status"""
        entry = ReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Agent",
            tokens=4500,
            max_tokens=5000,
            lines=450,
            max_lines=500,
            status="⚠️ Approaching token limit (90%)",
        )

        assert entry.get_severity() == 1

    def test_get_severity_error(self) -> None:
        """Test severity for error status"""
        entry = ReportEntry(
            file_path="test.md",
            line_number=42,
            file_type="Agent",
            tokens=6000,
            max_tokens=5000,
            lines=600,
            max_lines=500,
            status="❌ Exceeds token limit (6000/5000)",
        )

        assert entry.get_severity() == 2
