from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class AiStats:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def compute_token_count_accurate(self, text: str) -> int:
        """Compute token count for a given text using tiktoken if available"""
        try:
            import tiktoken  # pyright: ignore[reportMissingImports]

            encoder = tiktoken.get_encoding("cl100k_base")
            tokens = encoder.encode(text)
            return len(tokens)
        except ImportError:
            self.logger.log(
                LogLevel.WARNING,
                "tiktoken not found, using naive token count approximation.",
            )
            # Fallback to naive approximation if tiktoken is not available
            return len(text) // 4
