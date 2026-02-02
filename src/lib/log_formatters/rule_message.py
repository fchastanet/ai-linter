from lib.log_level import LogLevel


class RuleMessage:
    """Represents a log message with structured data"""

    def __init__(
        self,
        level: LogLevel,
        rule: str,
        message: str,
        file: str = "<unknown>",
        line_number: int | None = None,
        line_content: str | None = None,
        **kwargs: str,
    ):
        self.level = level
        self.rule = rule
        self.message = message
        self.file = file
        self.line_number = line_number
        self.line_content = line_content
        self.extra = kwargs
