"""Report entry for content length validation results"""

from dataclasses import dataclass


@dataclass
class ReportEntry:
    """Represents a report entry for a validated file"""

    file_path: str
    line_number: int
    file_type: str  # "Agent", "Prompt", "Skill"
    tokens: int
    max_tokens: int
    lines: int
    max_lines: int
    status: str  # "✅ Valid", "⚠️ Warning", "❌ Error"

    def get_severity(self) -> int:
        """Return numeric severity for sorting (0=valid, 1=warning, 2=error)"""
        if self.status.startswith("✅"):
            return 0
        elif self.status.startswith("⚠️"):
            return 1
        else:  # ❌
            return 2
