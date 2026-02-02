"""Factory for creating log formatters"""

from lib.log_format import LogFormat
from lib.log_formatters.base_log_formatter import BaseLogFormatter
from lib.log_formatters.file_digest_formatter import FileDigestFormatter
from lib.log_formatters.logfmt_formatter import LogfmtFormatter
from lib.log_formatters.yaml_formatter import YamlFormatter


class LogFormatterFactory:
    """Factory for creating log formatters"""

    _formatters: dict[LogFormat, type[BaseLogFormatter]] = {
        LogFormat.LOGFMT: LogfmtFormatter,
        LogFormat.FILE_DIGEST: FileDigestFormatter,
        LogFormat.YAML: YamlFormatter,
    }

    @staticmethod
    def create(format: LogFormat) -> BaseLogFormatter:
        """Create a formatter for the specified format"""
        formatter_class = LogFormatterFactory._formatters.get(format, FileDigestFormatter)
        return formatter_class()
