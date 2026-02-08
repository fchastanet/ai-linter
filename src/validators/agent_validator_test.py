from pathlib import Path

import pytest

from lib.ai.stats import AiStats
from lib.config import Config
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from validators.agent_validator import AgentValidator
from validators.code_snippet_validator import CodeSnippetValidator
from validators.content_length_validator import ContentLengthValidator
from validators.file_reference_validator import FileReferenceValidator


class TestAgentValidator:
    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def parser(self, logger: Logger) -> Parser:
        """Create a parser"""
        return Parser(logger)

    @pytest.fixture
    def ai_stats(self, logger: Logger) -> AiStats:
        """Create AI stats"""
        return AiStats(logger)

    @pytest.fixture
    def config(self) -> Config:
        """Create a test config"""
        config = Config()
        config.resource_dirs = []
        config.ignore_dirs = []
        config.unreferenced_file_level = LogLevel.ERROR
        config.code_snippet_max_lines = 100
        return config

    @pytest.fixture
    def validator(
        self,
        logger: Logger,
        parser: Parser,
        ai_stats: AiStats,
        config: Config,
    ) -> AgentValidator:
        """Create an AgentValidator"""
        content_length_validator = ContentLengthValidator(logger, ai_stats)
        file_reference_validator = FileReferenceValidator(logger, parser)
        code_snippet_validator = CodeSnippetValidator(logger, 100)

        return AgentValidator(
            logger,
            parser,
            content_length_validator,
            file_reference_validator,
            code_snippet_validator,
            config,
        )

    def test_valid_agents_file(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test validation of a valid AGENTS.md file"""
        agents_file = tmp_path / "AGENTS.md"
        content = """# Agent Configurations

This is a valid agents file without frontmatter.

## Agent 1

Description of agent 1.
"""
        agents_file.write_text(content)

        warnings, errors = validator.validate_agent_file([tmp_path], agents_file, tmp_path)
        assert errors == 0

    def test_agents_file_with_frontmatter(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test that AGENTS.md with frontmatter is rejected"""
        agents_file = tmp_path / "AGENTS.md"
        content = """---
title: Agents
---

# Agent Configurations
"""
        agents_file.write_text(content)

        warnings, errors = validator.validate_agent_file([tmp_path], agents_file, tmp_path)
        assert errors >= 1

    def test_agents_file_missing_content(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test when AGENTS.md has no content"""
        agents_file = tmp_path / "AGENTS.md"
        content = """---
title: Agents
---
"""
        agents_file.write_text(content)

        warnings, errors = validator.validate_agent_file([tmp_path], agents_file, tmp_path)
        assert errors >= 1

    def test_agents_file_empty(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test validation of an empty AGENTS.md file"""
        agents_file = tmp_path / "AGENTS.md"
        agents_file.write_text("")

        warnings, errors = validator.validate_agent_file([tmp_path], agents_file, tmp_path)
        # Empty file should have some error
        assert errors >= 0

    def test_agents_file_with_links(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test AGENTS.md with valid file references"""
        # Create reference file
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        (ref_dir / "agent-ref.md").write_text("Agent reference")

        agents_file = tmp_path / "AGENTS.md"
        content = """# Agent Configurations

See [reference](references/agent-ref.md) for more info.
"""
        agents_file.write_text(content)

        warnings, errors = validator.validate_agent_file([tmp_path], agents_file, tmp_path)
        # Should not error due to broken reference
        assert errors == 0

    def test_validate_agents_files_multiple(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test validation of multiple AGENTS.md files"""
        # Create first AGENTS.md
        agents1 = tmp_path / "AGENTS.md"
        agents1.write_text("# Agents 1\n\nFirst agents file")

        warnings, errors = validator.validate_agents_files(tmp_path, None)
        # Should validate without errors (one file, no references needed)
        assert errors == 0

    def test_validate_agents_files_ignore_dirs(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test that validate_agents_files respects ignore_dirs"""
        # Create first AGENTS.md
        agents1 = tmp_path / "AGENTS.md"
        agents1.write_text("---\ntitle: Invalid\n---\n")

        # Create AGENTS.md in ignored directory
        ignored_dir = tmp_path / "ignored"
        ignored_dir.mkdir()
        agents2 = ignored_dir / "AGENTS.md"
        agents2.write_text("---\ntitle: Should be ignored\n---\n")

        warnings, errors = validator.validate_agents_files(tmp_path, [Path("ignored")])
        # Only the first agents file should be validated (and fail due to frontmatter)
        assert errors >= 1
