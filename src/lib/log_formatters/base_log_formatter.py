"""Abstract base class for log formatters"""

from abc import ABC, abstractmethod
from typing import Any

from lib.log_format import LogFormat


class BaseLogFormatter(ABC):
    """Abstract base class for log formatters"""

    @abstractmethod
    def format(self, messages: list[dict[str, Any]]) -> str:
        """Format a list of messages for output"""
        pass

    @abstractmethod
    def get_format(self) -> LogFormat:
        """Return the LogFormat this formatter produces"""
        pass
