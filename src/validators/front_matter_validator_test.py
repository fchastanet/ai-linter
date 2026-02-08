from pathlib import Path

import pytest

from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from validators.front_matter_validator import FrontMatterValidator


class TestFrontMatterValidator:
    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def parser(self, logger: Logger) -> Parser:
        """Create a parser"""
        return Parser(logger)

    @pytest.fixture
    def validator(self, logger: Logger, parser: Parser) -> FrontMatterValidator:
        """Create a FrontMatterValidator"""
        return FrontMatterValidator(logger, parser)

    def test_validate_keys_valid(self, validator: FrontMatterValidator, tmp_path: Path) -> None:
        """Test validation of allowed keys"""
        test_file = tmp_path / "SKILL.md"
        frontmatter = {"name": "test-skill", "description": "A test skill"}
        allowed_properties = {"name", "description", "license"}

        warnings, errors = validator.validate_keys(frontmatter, test_file, allowed_properties, project_dir=tmp_path)
        assert errors == 0

    def test_validate_keys_unexpected(self, validator: FrontMatterValidator, tmp_path: Path) -> None:
        """Test validation with unexpected properties"""
        test_file = tmp_path / "SKILL.md"
        frontmatter = {"name": "test-skill", "invalid-prop": "value"}
        allowed_properties = {"name", "description"}

        warnings, errors = validator.validate_keys(frontmatter, test_file, allowed_properties, project_dir=tmp_path)
        assert warnings == 1  # Should have 1 warning for unexpected property

    def test_validate_name_valid_format(self, validator: FrontMatterValidator, tmp_path: Path) -> None:
        """Test validation of valid skill name format"""
        test_file = tmp_path / "SKILL.md"
        test_dir = tmp_path / "test-skill"
        test_dir.mkdir()

        frontmatter = {"name": "test-skill"}
        frontmatter_text = "name: test-skill\n"

        warnings, errors = validator.validate_name(
            frontmatter, test_file, frontmatter_text, test_dir, project_dir=tmp_path
        )
        assert errors == 0

    def test_validate_name_invalid_format(self, validator: FrontMatterValidator, tmp_path: Path) -> None:
        """Test validation of invalid skill name format"""
        test_file = tmp_path / "SKILL.md"
        test_dir = tmp_path / "TestSkill"
        test_dir.mkdir()

        frontmatter = {"name": "TestSkill"}  # Invalid: not lowercase with hyphens
        frontmatter_text = "name: TestSkill\n"

        warnings, errors = validator.validate_name(
            frontmatter, test_file, frontmatter_text, test_dir, project_dir=tmp_path
        )
        assert errors >= 1

    def test_validate_name_missing(self, validator: FrontMatterValidator, tmp_path: Path) -> None:
        """Test validation when name is missing"""
        test_file = tmp_path / "SKILL.md"
        test_dir = tmp_path / "test-skill"
        test_dir.mkdir()

        frontmatter: dict = {}  # Missing name
        frontmatter_text = ""

        warnings, errors = validator.validate_name(
            frontmatter, test_file, frontmatter_text, test_dir, project_dir=tmp_path
        )
        assert errors >= 1

    def test_validate_description_present(self, validator: FrontMatterValidator, tmp_path: Path) -> None:
        """Test validation when description is present"""
        test_file = tmp_path / "SKILL.md"
        frontmatter = {"description": "A test skill"}
        frontmatter_text = "description: A test skill\n"

        warnings, errors = validator.validate_description(
            frontmatter, test_file, frontmatter_text, project_dir=tmp_path
        )
        assert errors == 0

    def test_validate_description_missing(self, validator: FrontMatterValidator, tmp_path: Path) -> None:
        """Test validation when description is missing"""
        test_file = tmp_path / "SKILL.md"
        frontmatter: dict = {}  # Missing description
        frontmatter_text = ""

        warnings, errors = validator.validate_description(
            frontmatter, test_file, frontmatter_text, project_dir=tmp_path
        )
        assert errors >= 1

    def test_validate_description_too_long(self, validator: FrontMatterValidator, tmp_path: Path) -> None:
        """Test validation when description is too long"""
        test_file = tmp_path / "SKILL.md"
        # Create a description with over 1024 characters
        long_desc = "x" * 1025  # More than 1024 characters (max allowed)
        frontmatter = {"description": long_desc}
        frontmatter_text = f"description: {long_desc}\n"

        warnings, errors = validator.validate_description(
            frontmatter, test_file, frontmatter_text, project_dir=tmp_path
        )
        assert errors == 1  # Should have 1 error for description being too long
