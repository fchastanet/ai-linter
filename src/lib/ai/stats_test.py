from unittest.mock import MagicMock, patch

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

    @patch("tiktoken.get_encoding")
    def test_compute_token_count_with_tiktoken(self, mock_get_encoding: MagicMock, stats: AiStats) -> None:
        """Test token count computation when tiktoken is available"""
        # Mock the tiktoken encoder
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = ["Hello"] * 11  # 11 tokens
        mock_get_encoding.return_value = mock_encoder

        text = "Hello, this is a test text for token counting."
        result = stats.compute_token_count_accurate(text)

        # Result should be a positive integer
        assert isinstance(result, int)
        assert result > 0
        assert result == 11
        # Verify tiktoken was called
        mock_get_encoding.assert_called_once_with("cl100k_base")
        mock_encoder.encode.assert_called_once_with(text)

    @patch("tiktoken.get_encoding")
    def test_compute_token_count_empty_string(self, mock_get_encoding: MagicMock, stats: AiStats) -> None:
        """Test token count for empty string"""
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = []  # Empty list = 0 tokens
        mock_get_encoding.return_value = mock_encoder

        result = stats.compute_token_count_accurate("")

        assert isinstance(result, int)
        assert result == 0

    @patch("tiktoken.get_encoding")
    def test_compute_token_count_long_text(self, mock_get_encoding: MagicMock, stats: AiStats) -> None:
        """Test token count for longer text"""
        mock_encoder = MagicMock()
        # 50 repetitions should yield more than 100 tokens
        mock_encoder.encode.return_value = ["token"] * 250
        mock_get_encoding.return_value = mock_encoder

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

    @patch("tiktoken.get_encoding")
    def test_compute_token_count_special_characters(self, mock_get_encoding: MagicMock, stats: AiStats) -> None:
        """Test token count with special characters"""
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = ["token"] * 15
        mock_get_encoding.return_value = mock_encoder

        text = "Hello! @#$%^&*() [brackets] {braces}"
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 0

    @patch("tiktoken.get_encoding")
    def test_compute_token_count_unicode(self, mock_get_encoding: MagicMock, stats: AiStats) -> None:
        """Test token count with unicode characters"""
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = ["token"] * 12
        mock_get_encoding.return_value = mock_encoder

        text = "Hello 世界 مرحبا привет"
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 0

    @patch("tiktoken.get_encoding")
    def test_compute_token_count_multiline(self, mock_get_encoding: MagicMock, stats: AiStats) -> None:
        """Test token count with multiline text"""
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = ["token"] * 10
        mock_get_encoding.return_value = mock_encoder

        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 0

    @patch("tiktoken.get_encoding")
    def test_compute_token_count_numeric_text(self, mock_get_encoding: MagicMock, stats: AiStats) -> None:
        """Test token count with numeric text"""
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = ["token"] * 20
        mock_get_encoding.return_value = mock_encoder

        text = "1234567890 " * 10
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 0

    @patch("tiktoken.get_encoding")
    def test_compute_token_count_very_long(self, mock_get_encoding: MagicMock, stats: AiStats) -> None:
        """Test token count for very long text"""
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = ["token"] * 2000
        mock_get_encoding.return_value = mock_encoder

        text = "word " * 10000  # Create very long text
        result = stats.compute_token_count_accurate(text)

        assert isinstance(result, int)
        assert result > 1000  # Should be substantial number of tokens
