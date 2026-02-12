import pytest

from lib.ai.stats import AiStats
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class TestAiStats:
    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def stats(self, logger: Logger) -> AiStats:
        """Create an AiStats instance"""
        return AiStats(logger)

    def test_compute_token_count_with_tiktoken(self, stats: AiStats) -> None:
        """Test token count computation when tiktoken is available"""
        text = "Hello, this is a test text for token counting."
        result = stats.compute_token_count_accurate(text)

        # Result should be a positive integer
        assert isinstance(result, int)
        assert result > 0
        # For this text, tiktoken should return around 10-12 tokens
        assert result < 20

    def test_compute_token_count_empty_string(self, stats: AiStats) -> None:
        """Test token count for empty string"""
        result = stats.compute_token_count_accurate("")

        assert isinstance(result, int)
        assert result == 0

    def test_compute_token_count_long_text(self, stats: AiStats) -> None:
        """Test token count for longer text"""
        text = "This is a longer text. " * 50
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 0
        # For 50 repetitions of the phrase, should be several hundred tokens
        assert result > 100

    def test_ai_stats_initialization(self, logger: Logger) -> None:
        """Test AiStats initialization"""
        stats = AiStats(logger)

        assert stats.logger == logger
        assert isinstance(stats, AiStats)

    def test_compute_token_count_special_characters(self, stats: AiStats) -> None:
        """Test token count with special characters"""
        text = "Hello! @#$%^&*() [brackets] {braces}"
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 0

    def test_compute_token_count_unicode(self, stats: AiStats) -> None:
        """Test token count with unicode characters"""
        text = "Hello 世界 مرحبا привет"
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 0

    def test_compute_token_count_multiline(self, stats: AiStats) -> None:
        """Test token count with multiline text"""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 0

    def test_compute_token_count_numeric_text(self, stats: AiStats) -> None:
        """Test token count with numeric text"""
        text = "1234567890 " * 10
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 0

    def test_compute_token_count_very_long(self, stats: AiStats) -> None:
        """Test token count for very long text"""
        text = "word " * 10000  # Create very long text
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 1000  # Should be substantial number of tokens
