from pathlib import Path

import pytest

from lib.log.logger import Logger, LogLevel
from lib.parser import Parser
from validators.file_reference_validator import FileReferenceValidator
from validators.prompt_agent_validator import PromptAgentValidator


class TestPromptAgentValidator:
    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def parser(self, logger: Logger) -> Parser:
        """Create a parser"""
        return Parser(logger)

    @pytest.fixture
    def file_ref_validator(self, logger: Logger) -> FileReferenceValidator:
        """Create a file reference validator"""
        return FileReferenceValidator(logger)

    @pytest.fixture
    def validator(
        self, logger: Logger, parser: Parser, file_ref_validator: FileReferenceValidator
    ) -> PromptAgentValidator:
        """Create a prompt/agent validator"""
        return PromptAgentValidator(logger, parser, file_ref_validator, missing_agents_level=LogLevel.WARNING)

    def test_agents_md_missing(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test detection of missing AGENTS.md"""
        warnings, errors = validator.validate_agents_md_exists(tmp_path)
        assert warnings == 1
        assert errors == 0

    def test_agents_md_exists(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test that existing AGENTS.md doesn't generate warnings"""
        agents_file = tmp_path / "AGENTS.md"
        agents_file.write_text("# Agent Configuration")

        warnings, errors = validator.validate_agents_md_exists(tmp_path)
        assert warnings == 0
        assert errors == 0

    def test_extract_tool_references(self, validator: PromptAgentValidator) -> None:
        """Test extracting tool references"""
        content = """
tool: grep_search
allowed-tools: [read_file, write_file]
uses semantic_search
tool `file_search`
        """
        tools = validator.extract_tool_references(content)
        assert "grep_search" in tools
        assert "read_file" in tools
        assert "write_file" in tools
        assert "semantic_search" in tools
        assert "file_search" in tools

    def test_extract_skill_references(self, validator: PromptAgentValidator) -> None:
        """Test extracting skill references"""
        content = """
skill: python-testing
uses skill unit-test-helper
skill `typescript-linting`
        """
        skills = validator.extract_skill_references(content)
        assert "python-testing" in skills
        assert "unit-test-helper" in skills
        assert "typescript-linting" in skills

    def test_validate_short_file(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test validation of file within limits"""
        test_file = tmp_path / "test.md"
        content = "# Prompt\n\nShort content\n" * 10
        test_file.write_text(content)

        warnings, errors, metadata = validator.validate_prompt_or_agent_file(test_file, tmp_path)

        assert warnings == 0
        assert errors == 0
        assert "line_count" in metadata
        assert "token_count" in metadata

    def test_validate_long_file(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test validation of file exceeding line limit"""
        test_file = tmp_path / "test.md"
        content = "\n".join([f"Line {i}" for i in range(600)])
        test_file.write_text(content)

        warnings, errors, metadata = validator.validate_prompt_or_agent_file(test_file, tmp_path)

        assert warnings >= 1  # Should warn about line count
        assert metadata["line_count"] > 500

    def test_validate_high_token_count(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test validation of file with high token count"""
        test_file = tmp_path / "test.md"
        # Create content with many words
        content = " ".join([f"word{i}" for i in range(6000)])
        test_file.write_text(content)

        warnings, errors, metadata = validator.validate_prompt_or_agent_file(test_file, tmp_path)

        assert warnings >= 1  # Should warn about token count
        assert metadata["token_count"] > 5000

    def test_validate_with_file_references(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test validation with file references"""
        # Create a referenced file
        ref_file = tmp_path / "reference.txt"
        ref_file.write_text("content")

        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\n\n[Link](reference.txt)")

        warnings, errors, metadata = validator.validate_prompt_or_agent_file(test_file, tmp_path)

        assert "file_references" in metadata
        assert len(metadata["file_references"]) > 0

    def test_validate_prompt_directories(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test validation of prompt directories"""
        # Create .github/prompts directory
        prompts_dir = tmp_path / ".github" / "prompts"
        prompts_dir.mkdir(parents=True)

        # Create a prompt file
        prompt_file = prompts_dir / "test-prompt.md"
        prompt_file.write_text("# Test Prompt\n\nShort content")

        warnings, errors = validator.validate_prompt_agent_directories(
            tmp_path, prompt_dirs=[Path(".github/prompts")], agent_dirs=[]
        )

        # Should have warning for missing AGENTS.md
        assert warnings >= 1

    def test_validate_agent_directories(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test validation of agent directories"""
        # Create AGENTS.md to avoid warning
        (tmp_path / "AGENTS.md").write_text("# Agents")

        # Create .github/agents directory
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        # Create an agent file
        agent_file = agents_dir / "test-agent.md"
        agent_file.write_text("# Test Agent\n\ntool: grep_search\nskill: python-testing")

        warnings, errors = validator.validate_prompt_agent_directories(
            tmp_path, prompt_dirs=[], agent_dirs=[Path(".github/agents")]
        )

        assert errors == 0

    def test_nonexistent_directories(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test that nonexistent directories don't cause errors"""
        # Create AGENTS.md to avoid that warning
        (tmp_path / "AGENTS.md").write_text("# Agents")

        warnings, errors = validator.validate_prompt_agent_directories(
            tmp_path, prompt_dirs=[Path(".github/prompts")], agent_dirs=[Path(".github/agents")]
        )

        # Should not error, just skip missing directories
        assert errors == 0

    def test_metadata_extraction(self, validator: PromptAgentValidator, tmp_path: Path) -> None:
        """Test that metadata is correctly extracted"""
        test_file = tmp_path / "test.md"
        content = """# Test Prompt

tool: grep_search
tool: semantic_search
skill: python-testing
skill: react-hooks

[Reference](docs/guide.md)
"""
        test_file.write_text(content)

        warnings, errors, metadata = validator.validate_prompt_or_agent_file(test_file, tmp_path)

        assert len(metadata["tools"]) == 2
        assert "grep_search" in metadata["tools"]
        assert "semantic_search" in metadata["tools"]

        assert len(metadata["skills"]) == 2
        assert "python-testing" in metadata["skills"]
        assert "react-hooks" in metadata["skills"]

        assert "file_references" in metadata
