"""Adapter for tabulate library to generate formatted tables"""

from collections.abc import Iterable, Sequence
from typing import Any, Optional, Union

from tabulate import SEPARATING_LINE

from lib.log.log_formatters.report_entry import ReportEntry


class TabulateAdapter:
    """Adapter for generating formatted tables using tabulate library"""

    @staticmethod
    def generate_report_table(entries: list[ReportEntry]) -> str:
        """Generate a formatted table from report entries.

        Args:
            entries: List of ReportEntry objects

        Returns:
            Formatted table string
        """
        if not entries:
            return ""

        try:
            from tabulate import tabulate
        except ImportError:
            # Fallback to simple formatting if tabulate is not available
            return TabulateAdapter._generate_simple_table(entries)

        # Sort entries by severity then by file path
        sorted_entries = sorted(entries, key=lambda e: (e.get_severity(), e.file_path))

        # Prepare table data
        table_data = []
        total_tokens = 0
        total_lines = 0
        valid_count = 0
        warning_count = 0
        error_count = 0

        for entry in sorted_entries:
            table_data.append(
                [
                    entry.file_path,
                    entry.file_type,
                    f"{entry.tokens}/{entry.max_tokens}",
                    f"{entry.lines}/{entry.max_lines}",
                    entry.status,
                ]
            )
            total_tokens += entry.tokens
            total_lines += entry.lines

            if entry.status.startswith("✅"):
                valid_count += 1
            elif entry.status.startswith("⚠️"):
                warning_count += 1
            else:
                error_count += 1

        # Add summary row
        summary_status = []
        if valid_count > 0:
            summary_status.append(f"{valid_count} Valid")
        if warning_count > 0:
            summary_status.append(f"{warning_count} Warning{'s' if warning_count > 1 else ''}")
        if error_count > 0:
            summary_status.append(f"{error_count} Error{'s' if error_count > 1 else ''}")

        # Add a separating line before summary
        table_data.append(SEPARATING_LINE)  # type: ignore[arg-type]

        # Add summary row with totals and summary status
        table_data.append(
            [
                "Total",
                "",
                str(total_tokens),
                str(total_lines),
                ", ".join(summary_status),
            ]
        )

        headers = ["File Path", "Type", "Tokens", "Lines", "Status"]
        return tabulate(table_data, headers=headers, tablefmt="simple", maxcolwidths=[50, None, None, None, 30])

    @staticmethod
    def display_table(
        tabular_data: Any,
        headers: str | dict[str, str] | Sequence[str] = (),
        tablefmt: str = "simple",
        showindex: str = "default",
        disable_numparse: bool = False,
        colalign: Optional[Sequence[Optional[str]]] = None,
        maxcolwidths: Optional[Union[int, Sequence[Optional[int]]]] = None,
        rowalign: str | Iterable[str] | None = None,
        maxheadercolwidths: int | Iterable[int] | None = None,
    ) -> str:
        """Display the generated table (can be extended for different output formats)"""
        try:
            from tabulate import tabulate
        except ImportError:
            print("Tabulate library is not installed, cannot display table")
            return ""
        return tabulate(
            tabular_data,
            headers=headers,
            tablefmt=tablefmt,
            showindex=showindex,
            disable_numparse=disable_numparse,
            colalign=colalign,
            maxcolwidths=maxcolwidths,
            rowalign=rowalign,
            maxheadercolwidths=maxheadercolwidths,
        )

    @staticmethod
    def _generate_simple_table(entries: list[ReportEntry]) -> str:
        """Generate a simple text table without tabulate library.

        Fallback method when tabulate is not installed.
        """
        if not entries:
            return ""

        # Sort by severity then by file path
        sorted_entries = sorted(entries, key=lambda e: (e.get_severity(), e.file_path))

        # Calculate column widths
        max_path = max(len(e.file_path) for e in sorted_entries)
        max_path = max(max_path, len("File Path"))
        max_status = max(len(e.status) for e in sorted_entries)
        max_status = max(max_status, len("Status"))

        # Build table
        lines = []
        header = (
            f"| {'File Path':<{max_path}} | {'Type':<8} | {'Tokens':<15} | "
            f"{'Lines':<15} | {'Status':<{max_status}} |"
        )
        lines.append(header)

        total_tokens = 0
        total_lines = 0
        valid_count = 0
        warning_count = 0
        error_count = 0

        for entry in sorted_entries:
            tokens_str = f"{entry.tokens}/{entry.max_tokens}"
            lines_str = f"{entry.lines}/{entry.max_lines}"
            line = (
                f"| {entry.file_path:<{max_path}} | {entry.file_type:<8} | "
                f"{tokens_str:<15} | {lines_str:<15} | {entry.status:<{max_status}} |"
            )
            lines.append(line)

            total_tokens += entry.tokens
            total_lines += entry.lines

            if entry.status.startswith("✅"):
                valid_count += 1
            elif entry.status.startswith("⚠️"):
                warning_count += 1
            else:
                error_count += 1

        # Summary
        summary_status = []
        if valid_count > 0:
            summary_status.append(f"{valid_count} Valid")
        if warning_count > 0:
            summary_status.append(f"{warning_count} Warning{'s' if warning_count > 1 else ''}")
        if error_count > 0:
            summary_status.append(f"{error_count} Error{'s' if error_count > 1 else ''}")

        summary_status_str = ", ".join(summary_status)
        summary_line = (
            f"| {'Total':<{max_path}} | {'':<8} | {total_tokens:<15} | "
            f"{total_lines:<15} | {summary_status_str:<{max_status}} |"
        )
        lines.append(summary_line)

        return "\n".join(lines)
