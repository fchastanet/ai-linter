from pathlib import Path

import pytest

from lib.ai.stats import AiStats
from lib.config import Config
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from validators.code_snippet_validator import CodeSnippetValidator
from validators.content_length_validator import ContentLengthValidator
from validators.file_reference_validator import FileReferenceValidator
from validators.front_matter_validator import FrontMatterValidator
from validators.skill_validator import SkillValidator


class TestSkillValidator:
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
    ) -> SkillValidator:
        """Create a SkillValidator"""
        content_length_validator = ContentLengthValidator(logger, ai_stats)
        file_ref_validator = FileReferenceValidator(logger, parser)
        front_matter_validator = FrontMatterValidator(logger, parser)
        code_snippet_validator = CodeSnippetValidator(logger, 100)

        return SkillValidator(
            logger,
            parser,
            content_length_validator,
            file_ref_validator,
            front_matter_validator,
            code_snippet_validator,
            config,
        )

    def test_skill_not_found(self, validator: SkillValidator, tmp_path: Path) -> None:
        """Test validation when SKILL.md is missing"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        warnings, errors = validator.validate_skill(skill_dir, tmp_path)
        assert errors == 1  # Should have 1 error

    def test_valid_skill(self, validator: SkillValidator, tmp_path: Path) -> None:
        """Test validation of a valid skill"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        content = """---
name: test-skill
description: A test skill
---

# Test Skill

This is a test skill with valid content.
"""
        skill_md.write_text(content)

        warnings, errors = validator.validate_skill(skill_dir, tmp_path)
        # Should pass validation (no errors expected)
        assert errors <= 0

    def test_skill_missing_name(self, validator: SkillValidator, tmp_path: Path) -> None:
        """Test validation when name is missing"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        content = """---
description: A test skill
---

# Test Skill
"""
        skill_md.write_text(content)

        warnings, errors = validator.validate_skill(skill_dir, tmp_path)
        assert errors >= 1

    def test_skill_missing_description(self, validator: SkillValidator, tmp_path: Path) -> None:
        """Test validation when description is missing"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        content = """---
name: test-skill
---

# Test Skill
"""
        skill_md.write_text(content)

        warnings, errors = validator.validate_skill(skill_dir, tmp_path)
        assert errors >= 1

    def test_invalid_frontmatter(self, validator: SkillValidator, tmp_path: Path) -> None:
        """Test validation with invalid YAML frontmatter"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        # Invalid YAML with unclosed quote
        content = """---
name: test-skill
description: "Unclosed quote
---

Content
"""
        skill_md.write_text(content)

        warnings, errors = validator.validate_skill(skill_dir, tmp_path)
        assert errors >= 1

    def test_deduce_project_root(self, validator: SkillValidator, tmp_path: Path) -> None:
        """Test deduction of project root directory from skill directory"""
        skill_dir = tmp_path / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)

        project_root = validator.deduce_project_root_dir_from_skill_dir(skill_dir)
        # The method expects 3 levels up from skill directory
        expected_root = skill_dir.parent.parent.parent
        assert project_root == expected_root
