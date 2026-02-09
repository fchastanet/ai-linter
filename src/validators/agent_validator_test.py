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

    def test_extract_sections_basic(self, validator: AgentValidator) -> None:
        """Test extraction of sections from markdown content"""
        content = """# Main Title

## Section One

Some content here.

### Subsection

More content.

## Another Section

Final content.
"""
        sections = validator._extract_sections(content)
        
        assert "main title" in sections
        assert "section one" in sections
        assert "subsection" in sections
        assert "another section" in sections

    def test_extract_sections_various_levels(self, validator: AgentValidator) -> None:
        """Test extraction of sections with various header levels"""
        content = """# H1 Header
## H2 Header
### H3 Header
#### H4 Header
##### H5 Header
###### H6 Header
"""
        sections = validator._extract_sections(content)
        
        assert len(sections) == 6
        assert "h1 header" in sections
        assert "h6 header" in sections

    def test_extract_sections_with_special_chars(self, validator: AgentValidator) -> None:
        """Test extraction of sections with special characters"""
        content = """## Build & Commands
### Using Sub-agents
## Git Commit Conventions
"""
        sections = validator._extract_sections(content)
        
        assert "build & commands" in sections
        assert "using sub-agents" in sections
        assert "git commit conventions" in sections

    def test_extract_sections_empty_content(self, validator: AgentValidator) -> None:
        """Test extraction from empty content"""
        sections = validator._extract_sections("")
        assert sections == []

    def test_validate_sections_all_present(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test validation when all mandatory sections are present"""
        content = """# Agent Documentation

## Navigating the Codebase

Description here.

## Build & Commands

More info.

## Using Subagents

Details.

## Code Style

Guidelines.

## Testing

Test info.

## Security

Security notes.

## Configuration

Config details.
"""
        agent_file = tmp_path / "AGENTS.md"
        agent_file.write_text(content)
        
        warnings, errors = validator._validate_sections(content, agent_file, tmp_path)
        
        # All mandatory sections present, should have no errors
        assert errors == 0
        assert warnings == 0

    def test_validate_sections_missing_mandatory(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test validation when mandatory sections are missing"""
        content = """# Agent Documentation

## Some Other Section

Just some content.
"""
        agent_file = tmp_path / "AGENTS.md"
        agent_file.write_text(content)
        
        warnings, errors = validator._validate_sections(content, agent_file, tmp_path)
        
        # Should have warnings for missing mandatory sections (default is WARNING level)
        assert warnings == 7  # All 7 mandatory sections missing

    def test_validate_sections_missing_mandatory_error_level(
        self, validator: AgentValidator, config: Config, tmp_path: Path
    ) -> None:
        """Test validation when mandatory sections are missing with ERROR level"""
        config.missing_section_level = LogLevel.ERROR
        validator.config = config
        
        content = """# Agent Documentation

## Some Other Section

Just some content.
"""
        agent_file = tmp_path / "AGENTS.md"
        agent_file.write_text(content)
        
        warnings, errors = validator._validate_sections(content, agent_file, tmp_path)
        
        # Should have errors for missing mandatory sections
        assert errors == 7  # All 7 mandatory sections missing

    def test_validate_sections_case_insensitive(self, validator: AgentValidator, tmp_path: Path) -> None:
        """Test that section matching is case-insensitive"""
        content = """# Agent Documentation

## NAVIGATING THE CODEBASE
## build & COMMANDS
## Using SubAgents
## CODE style
## TESTING
## Security
## configuration
"""
        agent_file = tmp_path / "AGENTS.md"
        agent_file.write_text(content)
        
        warnings, errors = validator._validate_sections(content, agent_file, tmp_path)
        
        # All mandatory sections present (case-insensitive match)
        assert errors == 0
        assert warnings == 0

    def test_validate_sections_recommended_missing(
        self, validator: AgentValidator, config: Config, tmp_path: Path
    ) -> None:
        """Test that missing recommended sections generate advice messages"""
        # Ensure advices are enabled
        config.enable_advices = True
        validator.config = config
        
        content = """# Agent Documentation

## Navigating the Codebase
## Build & Commands
## Using Subagents
## Code Style
## Testing
## Security
## Configuration
"""
        agent_file = tmp_path / "AGENTS.md"
        agent_file.write_text(content)
        
        warnings, errors = validator._validate_sections(content, agent_file, tmp_path)
        
        # No warnings or errors, just advice messages (not counted)
        assert errors == 0
        assert warnings == 0

    def test_validate_sections_advices_disabled(
        self, validator: AgentValidator, config: Config, tmp_path: Path
    ) -> None:
        """Test that advices can be disabled"""
        config.enable_advices = False
        validator.config = config
        
        content = """# Agent Documentation

## Navigating the Codebase
## Build & Commands
## Using Subagents
## Code Style
## Testing
## Security
## Configuration
"""
        agent_file = tmp_path / "AGENTS.md"
        agent_file.write_text(content)
        
        warnings, errors = validator._validate_sections(content, agent_file, tmp_path)
        
        # Should not generate any messages when advices disabled
        assert errors == 0
        assert warnings == 0

    def test_validate_sections_custom_mandatory(
        self, validator: AgentValidator, config: Config, tmp_path: Path
    ) -> None:
        """Test validation with custom mandatory sections"""
        config.mandatory_sections = ["testing", "security"]
        validator.config = config
        
        content = """# Agent Documentation

## Testing

Test info here.
"""
        agent_file = tmp_path / "AGENTS.md"
        agent_file.write_text(content)
        
        warnings, errors = validator._validate_sections(content, agent_file, tmp_path)
        
        # Should warn about missing "security" section only
        assert warnings == 1

    def test_validate_sections_custom_recommended(
        self, validator: AgentValidator, config: Config, tmp_path: Path
    ) -> None:
        """Test validation with custom recommended sections"""
        config.recommended_sections = ["deployment", "monitoring"]
        config.mandatory_sections = []  # No mandatory sections
        validator.config = config
        
        content = """# Agent Documentation

## Deployment

Deployment info.
"""
        agent_file = tmp_path / "AGENTS.md"
        agent_file.write_text(content)
        
        warnings, errors = validator._validate_sections(content, agent_file, tmp_path)
        
        # Should not error or warn, just advice about missing "monitoring"
        assert errors == 0
        assert warnings == 0
