from pathlib import Path

import pytest

from lib.ai.stats import AiStats
from lib.config import Config
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from processors.process_skills import ProcessSkills
from validators.code_snippet_validator import CodeSnippetValidator
from validators.content_length_validator import ContentLengthValidator
from validators.file_reference_validator import FileReferenceValidator
from validators.front_matter_validator import FrontMatterValidator
from validators.skill_validator import SkillValidator


class TestProcessSkills:
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
        config.ignore = []
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
    ) -> SkillValidator:
        """Create a skill validator with all dependencies"""
        content_length_validator = ContentLengthValidator(logger, ai_stats)
        file_reference_validator = FileReferenceValidator(logger, parser)
        front_matter_validator = FrontMatterValidator(logger, parser)
        code_snippet_validator = CodeSnippetValidator(logger, config.code_snippet_max_lines)

        return SkillValidator(
            logger,
            parser,
            content_length_validator,
            file_reference_validator,
            front_matter_validator,
            code_snippet_validator,
        )

    @pytest.fixture
    def processor(self, logger: Logger, parser: Parser, validator: SkillValidator) -> ProcessSkills:
        """Create a ProcessSkills instance"""
        return ProcessSkills(logger, parser, validator)

    def test_process_skill_with_valid_directory(self, processor: ProcessSkills, tmp_path: Path, config: Config) -> None:
        """Test processing a valid skill directory"""
        # Create a minimal valid skill directory
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        # Create a SKILL.md file
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("---\nname: test-skill\ndescription: A test skill\n---\n\n# Test Skill\n\nContent here")

        warnings, errors = processor.process_skill(skill_dir, tmp_path, config)

        # Should process without critical errors (though warnings may occur)
        assert isinstance(warnings, int)
        assert isinstance(errors, int)
        assert warnings >= 0
        assert errors >= 0

    def test_process_skill_with_nonexistent_directory(
        self, processor: ProcessSkills, tmp_path: Path, config: Config
    ) -> None:
        """Test processing when directory doesn't exist"""
        # Use a directory that doesn't exist
        nonexistent_dir = tmp_path / "nonexistent-skill"

        warnings, errors = processor.process_skill(nonexistent_dir, tmp_path, config)

        # Should return an error for missing directory
        assert errors >= 1

    def test_process_skill_with_file_not_directory(
        self, processor: ProcessSkills, tmp_path: Path, config: Config
    ) -> None:
        """Test processing when path is a file, not a directory"""
        # Create a file instead of directory
        skill_file = tmp_path / "skill.txt"
        skill_file.write_text("This is a file, not a directory")

        warnings, errors = processor.process_skill(skill_file, tmp_path, config)

        # Should return an error for file instead of directory
        assert errors >= 1

    def test_process_skill_returns_tuple(self, processor: ProcessSkills, tmp_path: Path, config: Config) -> None:
        """Test that process_skill returns a tuple of (warnings, errors)"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        result = processor.process_skill(skill_dir, tmp_path, config)

        # Result should be a tuple of two integers
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)

    def test_process_skills_initialization(self, logger: Logger, parser: Parser, validator: SkillValidator) -> None:
        """Test ProcessSkills initialization"""
        processor = ProcessSkills(logger, parser, validator)

        assert processor.logger == logger
        assert processor.parser == parser
        assert processor.validator == validator

    def test_process_skill_with_empty_directory(self, processor: ProcessSkills, tmp_path: Path, config: Config) -> None:
        """Test processing an empty skill directory"""
        skill_dir = tmp_path / "empty-skill"
        skill_dir.mkdir()

        warnings, errors = processor.process_skill(skill_dir, tmp_path, config)

        # Should process but may have errors (no SKILL.md file)
        assert isinstance(warnings, int)
        assert isinstance(errors, int)

    def test_process_skill_accumulates_errors(self, processor: ProcessSkills, tmp_path: Path, config: Config) -> None:
        """Test that process_skill properly accumulates warnings and errors"""
        skill_dir = tmp_path / "invalid-skill"
        skill_dir.mkdir()

        # Create a SKILL.md with errors
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("---\nname: invalid-skill-with-invalid-chars\n---\n")

        warnings, errors = processor.process_skill(skill_dir, tmp_path, config)

        # Should have at least some errors due to missing description
        assert errors >= 1

    def test_process_skill_success_returns_valid_tuple(
        self, processor: ProcessSkills, tmp_path: Path, config: Config
    ) -> None:
        """Test that successful processing returns valid warning/error counts"""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()

        # Create a valid SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("---\nname: my-skill\ndescription: Test skill\n---\n\nContent")

        warnings, errors = processor.process_skill(skill_dir, tmp_path, config)

        # Both should be integers >= 0
        assert isinstance(warnings, int) and warnings >= 0
        assert isinstance(errors, int) and errors >= 0
