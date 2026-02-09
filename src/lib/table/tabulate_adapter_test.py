"""Unit tests for TabulateAdapter"""

from lib.log.log_formatters.report_entry import ReportEntry
from lib.table.tabulate_adapter import TabulateAdapter


class TestTabulateAdapter:
    """Test TabulateAdapter table generation"""

    def test_generate_report_table_empty(self) -> None:
        """Test generating report table with no entries"""
        table = TabulateAdapter.generate_report_table([])
        assert table == ""

    def test_generate_report_table_single_entry(self) -> None:
        """Test generating report table with single entry"""
        entries = [
            ReportEntry(
                file_path="test.md",
                line_number=42,
                file_type="Agent",
                tokens=100,
                max_tokens=5000,
                lines=10,
                max_lines=500,
                status="✅ Valid",
            )
        ]

        table = TabulateAdapter.generate_report_table(entries)

        assert "test.md" in table
        assert "Agent" in table
        assert "100/5000" in table
        assert "10/500" in table
        assert "✅ Valid" in table
        assert "Total" in table

    def test_generate_report_table_multiple_entries(self) -> None:
        """Test generating report table with multiple entries"""
        entries = [
            ReportEntry(
                file_path="agent1.md",
                line_number=42,
                file_type="Agent",
                tokens=100,
                max_tokens=5000,
                lines=10,
                max_lines=500,
                status="✅ Valid",
            ),
            ReportEntry(
                file_path="prompt1.md",
                line_number=42,
                file_type="Prompt",
                tokens=4500,
                max_tokens=5000,
                lines=450,
                max_lines=500,
                status="⚠️ Approaching token limit (90%)",
            ),
            ReportEntry(
                file_path="agent2.md",
                line_number=42,
                file_type="Agent",
                tokens=6000,
                max_tokens=5000,
                lines=600,
                max_lines=500,
                status="❌ Exceeds token limit (6000/5000)",
            ),
        ]

        table = TabulateAdapter.generate_report_table(entries)

        # Check all entries are present
        assert "agent1.md" in table
        assert "prompt1.md" in table
        assert "agent2.md" in table

        # Check summary
        assert "Total" in table
        assert "1 Valid" in table or "1 Valid," in table
        assert "1 Warning" in table or "1 Warning," in table
        assert "1 Error" in table or "1 Error," in table

    def test_generate_report_table_sorting(self) -> None:
        """Test that entries are sorted by severity"""
        entries = [
            ReportEntry(
                file_path="error.md",
                line_number=42,
                file_type="Agent",
                tokens=6000,
                max_tokens=5000,
                lines=600,
                max_lines=500,
                status="❌ Exceeds token limit",
            ),
            ReportEntry(
                file_path="valid.md",
                line_number=42,
                file_type="Agent",
                tokens=100,
                max_tokens=5000,
                lines=10,
                max_lines=500,
                status="✅ Valid",
            ),
            ReportEntry(
                file_path="warning.md",
                line_number=42,
                file_type="Prompt",
                tokens=4500,
                max_tokens=5000,
                lines=450,
                max_lines=500,
                status="⚠️ Approaching token limit",
            ),
        ]

        table = TabulateAdapter.generate_report_table(entries)

        # Find positions of each file
        valid_pos = table.find("valid.md")
        warning_pos = table.find("warning.md")
        error_pos = table.find("error.md")

        # Check that they are in correct order (valid < warning < error)
        assert valid_pos < warning_pos < error_pos

    def test_generate_simple_table_fallback(self) -> None:
        """Test simple table generation (fallback without tabulate)"""
        entries = [
            ReportEntry(
                file_path="test.md",
                line_number=42,
                file_type="Agent",
                tokens=100,
                max_tokens=5000,
                lines=10,
                max_lines=500,
                status="✅ Valid",
            )
        ]

        table = TabulateAdapter._generate_simple_table(entries)

        assert "test.md" in table
        assert "Agent" in table
        assert "100/5000" in table
        assert "10/500" in table
        assert "✅ Valid" in table
        assert "Total" in table
