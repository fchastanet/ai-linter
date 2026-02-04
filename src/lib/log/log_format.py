"""Log format enumeration"""

from enum import Enum


class LogFormat(Enum):
    """Available logging format options"""

    LOGFMT = "logfmt"
    FILE_DIGEST = "file-digest"
    YAML = "yaml"

    @classmethod
    def from_string(cls, value: str | None) -> "LogFormat":
        """Convert a string to a LogFormat enum (case-insensitive)."""
        if isinstance(value, cls):
            return value
        if value is None:
            return cls.FILE_DIGEST
        key = str(value).strip().lower()
        for member in cls:
            if member.value == key:
                return member
        # Fallback to FILE_DIGEST if unknown
        return cls.FILE_DIGEST
