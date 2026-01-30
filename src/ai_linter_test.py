import os
import sys
import unittest

from aiLinter import AI_LINTER_VERSION

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestAILinter(unittest.TestCase):
    """Basic tests for AI Linter"""

    def test_version(self) -> None:
        """Test that version is defined"""
        self.assertIsNotNone(AI_LINTER_VERSION)
        self.assertTrue(isinstance(AI_LINTER_VERSION, str))
        self.assertTrue(len(AI_LINTER_VERSION) > 0)

    def test_import(self) -> None:
        """Test that main modules can be imported"""
        try:
            from lib.config import load_config  # noqa: F401
            from lib.log import Logger  # noqa: F401
            from lib.parser import Parser  # noqa: F401
            from validators.agent_validator import AgentValidator  # noqa: F401
            from validators.skill_validator import SkillValidator  # noqa: F401

            self.assertTrue(True, "All imports successful")
        except ImportError as e:
            self.fail(f"Import failed: {e}")


if __name__ == "__main__":
    unittest.main()
