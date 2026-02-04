"""Abstract base class for log formatters"""

from abc import ABC, abstractmethod

from lib.log.log_format import LogFormat
from lib.log.log_formatters.rule_message import RuleMessage


class BaseLogFormatter(ABC):
    """Abstract base class for log formatters"""

    @abstractmethod
    def format(self, messages: list[RuleMessage]) -> str:
        """Format a list of messages for output"""
        pass

    @abstractmethod
    def get_format(self) -> LogFormat:
        """Return the LogFormat this formatter produces"""
        pass
