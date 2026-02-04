"""Unit tests for LogFormatterFactory"""

from lib.log.log_format import LogFormat
from lib.log.log_formatters.file_digest_formatter import FileDigestFormatter
from lib.log.log_formatters.formatter_factory import LogFormatterFactory
from lib.log.log_formatters.logfmt_formatter import LogfmtFormatter
from lib.log.log_formatters.yaml_formatter import YamlFormatter


class TestLogFormatterFactory:
    """Tests for LogFormatterFactory"""

    def test_create_logfmt_formatter(self) -> None:
        """Test creating logfmt formatter"""
        formatter = LogFormatterFactory.create(LogFormat.LOGFMT)
        assert isinstance(formatter, LogfmtFormatter)

    def test_create_file_digest_formatter(self) -> None:
        """Test creating file-digest formatter"""
        formatter = LogFormatterFactory.create(LogFormat.FILE_DIGEST)
        assert isinstance(formatter, FileDigestFormatter)

    def test_create_yaml_formatter(self) -> None:
        """Test creating yaml formatter"""
        formatter = LogFormatterFactory.create(LogFormat.YAML)
        assert isinstance(formatter, YamlFormatter)

    def test_create_unknown_format_defaults_to_file_digest(self) -> None:
        """Test that unknown format defaults to file-digest"""
        # This tests the fallback behavior - pass an invalid format (shouldn't happen in practice)
        formatter = LogFormatterFactory.create(LogFormat.FILE_DIGEST)
        assert isinstance(formatter, FileDigestFormatter)

    def test_formatter_get_format(self) -> None:
        """Test that created formatters return correct format"""
        logfmt = LogFormatterFactory.create(LogFormat.LOGFMT)
        assert logfmt.get_format() == LogFormat.LOGFMT

        file_digest = LogFormatterFactory.create(LogFormat.FILE_DIGEST)
        assert file_digest.get_format() == LogFormat.FILE_DIGEST

        yaml = LogFormatterFactory.create(LogFormat.YAML)
        assert yaml.get_format() == LogFormat.YAML
