import os
from pathlib import Path

from lib.log import Logger, LogLevel
from lib.parser import Parser
from validators.file_reference_validator import FileReferenceValidator
from validators.front_matter_validator import FrontMatterValidator


class SkillValidator:
    MAX_SKILL_CONTENT_TOKEN_COUNT = 5000  # Maximum allowed token count for skill content
    MAX_SKILL_CONTENT_LINES_COUNT = 500  # Maximum allowed lines in skill content
    ALLOWED_PROPERTIES = {
        "name",
        "description",
        "license",
        "allowed-tools",
        "metadata",
        "compatibility",
    }

    def __init__(
        self,
        logger: Logger,
        parser: Parser,
        file_ref_validator: FileReferenceValidator,
        front_matter_validator: FrontMatterValidator,
    ):
        self.logger = logger
        self.parser = parser
        self.file_ref_validator = file_ref_validator
        self.front_matter_validator = front_matter_validator

    def validate_skill(self, skill_path: str | Path) -> tuple[int, int]:
        """Basic validation of a skill"""
        skill_path = Path(skill_path)
        project_root_dir = self.deduce_project_root_dir_from_skill_dir(skill_path)

        # Check SKILL.md exists
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            self.logger.log(
                LogLevel.ERROR,
                "skill-not-found",
                "SKILL.md not found",
                skill_md,
            )
            return 1, 0

        frontmatter_text, skill_content = self.parser.parse_content_and_frontmatter(skill_md)
        if frontmatter_text is None or skill_content is None:
            return 1, 0

        frontmatter, warning_count, error_count = self.parser.parse_frontmatter(frontmatter_text, skill_md)
        if error_count > 0:
            return warning_count, error_count

        if frontmatter is None:
            self.logger.log(
                LogLevel.ERROR,
                "skill-frontmatter-missing",
                "Frontmatter is missing or invalid in SKILL.md",
                skill_md,
            )
            return warning_count, error_count + 1

        nb_warnings = 0
        nb_errors = 0
        line_number = 2  # Starting line number for frontmatter

        # Check for unexpected properties (excluding nested keys under metadata)
        prop_warnings, prop_errors = self.front_matter_validator.validate_keys(
            frontmatter,
            skill_md,
            self.ALLOWED_PROPERTIES,
            line_number=line_number,
        )
        nb_warnings += prop_warnings
        nb_errors += prop_errors

        name_warnings, name_errors = self.front_matter_validator.validate_name(
            frontmatter, skill_md, frontmatter_text, skill_path, line_number=line_number
        )
        nb_warnings += name_warnings
        nb_errors += name_errors

        desc_warnings, desc_errors = self.front_matter_validator.validate_description(
            frontmatter, skill_md, frontmatter_text, line_number=line_number
        )
        nb_warnings += desc_warnings
        nb_errors += desc_errors

        # Check skill content length (max 8192 characters per spec)
        line_number = frontmatter_text.count("\n") + 3

        # Validate skill content length
        nb_warnings_content, nb_errors_content = self.file_ref_validator.validate_content_length(
            skill_content,
            skill_md,
            line_number,
            self.MAX_SKILL_CONTENT_TOKEN_COUNT,
            self.MAX_SKILL_CONTENT_LINES_COUNT,
        )
        nb_warnings += nb_warnings_content
        nb_errors += nb_errors_content

        # Validate file references in skill content
        nb_warnings_ref, nb_errors_ref = self.file_ref_validator.validate_content_file_references(
            [skill_path, project_root_dir], skill_path, skill_content, line_number
        )
        nb_warnings += nb_warnings_ref
        nb_errors += nb_errors_ref

        return nb_warnings, nb_errors

    def deduce_project_root_dir_from_skill_dir(self, skill_dir: str | Path) -> str:
        """Deduces the project root directory from a skill directory"""
        skill_path = Path(skill_dir)
        # Assume project root is three levels up from skill directory
        return os.path.realpath(skill_path.parent.parent.parent)
