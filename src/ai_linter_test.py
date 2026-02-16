import os
import sys
import unittest

import pytest

from ai_linter import AI_LINTER_VERSION
from lib.config import Arguments

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestAILinter:
    """Basic tests for AI Linter"""

    def test_version(self) -> None:
        """Test that version is defined"""
        assert AI_LINTER_VERSION is not None
        assert isinstance(AI_LINTER_VERSION, str)
        assert len(AI_LINTER_VERSION) > 0

    def test_import(self) -> None:
        """Test that main modules can be imported"""
        try:
            from lib.config import load_config  # noqa: F401
            from lib.log.logger import Logger  # noqa: F401
            from lib.parser import Parser  # noqa: F401
            from validators.agent_validator import AgentValidator  # noqa: F401
            from validators.skill_validator import SkillValidator  # noqa: F401

            assert True, "All imports successful"
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")

    @pytest.mark.parametrize(
        "skills",
        [
            (True),
            (False),
        ],
    )
    def test_validate_at_least_one_agent_should_exist_in_project_directory(
        self, capsys: pytest.CaptureFixture, skills: bool
    ) -> None:
        """Test that at least one agent exists in the project directory"""
        # create one temp directory with no files
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            # call ai_linter
            from ai_linter import validate  # noqa: F401
            from lib.config import Config  # noqa: F401
            from lib.log.log_format import LogFormat  # noqa: F401
            from lib.log.log_level import LogLevel  # noqa: F401

            # We expect one warning about no agents found, but the process should complete successfully
            try:
                args = Arguments(
                    skills=skills,
                    directories=[temp_dir],
                    config_file=None,
                    log_level=LogLevel.INFO,
                    log_format=LogFormat.FILE_DIGEST,
                    max_warnings=10,
                    ignore=None,
                )
                nb_warnings, nb_errors = validate(args)
                out, err = capsys.readouterr()
                sys.stdout.write(out)
                sys.stderr.write(err)
                assert "no-agents-found (WARNING): No AGENTS.md file found in the project directory" in out

                # check output for warning about no agents found
                assert 0 == nb_errors, f"Expected no errors, but got {nb_errors} errors"
                assert 1 == nb_warnings, "Expected one warning about no agents found"
            except Exception as e:
                pytest.fail(f"Process failed when no agents were found: {e}")


if __name__ == "__main__":
    unittest.main()
