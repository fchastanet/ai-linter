import re
from pathlib import Path

from lib.log import Logger, LogLevel
from lib.parser import Parser


class FrontMatterValidator:
    # Constants for validation
    # @see https://agentskills.io/specification
    MAX_NAME_LENGTH = 64  # Maximum allowed length for name
    MAX_DESCRIPTION_LENGTH = 1024  # Maximum allowed length for description
    MAX_DESCRIPTION_TOKEN_COUNT = 100  # Maximum allowed token count for description

    def __init__(self, logger: Logger, parser: Parser):
        self.logger = logger
        self.parser = parser

    def validate_keys(
        self, frontmatter: dict, file: str | Path, allowed_keys: set[str], line_number: int = 1
    ) -> tuple[int, int]:
        """Validate that frontmatter contains only allowed keys"""
        unexpected_keys = set(frontmatter.keys()) - allowed_keys
        if unexpected_keys:
            self.logger.log(
                LogLevel.WARNING,
                "unexpected-properties",
                f"Unexpected key(s) in frontmatter: {', '.join(sorted(unexpected_keys))}. ",
                file=file,
                line_number=line_number,
                detail=f"Allowed properties are: {', '.join(sorted(allowed_keys))}",
            )
            return 1, 0
        return 0, 0

    def validate_name(
        self, frontmatter: dict, file: str | Path, frontmatter_text: str, file_path: Path, line_number: int = 2
    ) -> tuple[int, int]:
        # Check required fields
        if "name" not in frontmatter:
            self.logger.log(
                LogLevel.ERROR,
                "missing-name",
                "Missing 'name' in frontmatter",
                file,
                line_number=line_number,
            )
            return 0, 1

        # Extract name for validation
        name = frontmatter.get("name", "")
        if name is None or not isinstance(name, str):
            self.logger.log(
                LogLevel.ERROR,
                "invalid-name-type",
                f"Name must be a string, got {type(name).__name__}",
                file,
                line_number=line_number,
            )
            return 0, 1

        nb_warnings = 0
        nb_errors = 0
        name = name.strip()
        if not name:
            self.logger.log(
                LogLevel.ERROR,
                "empty-name",
                "Name in frontmatter cannot be empty",
                file,
                line_number=line_number,
            )
            return 0, 1

        line_number += self.parser.get_frontmatter_line_number(frontmatter_text, "name") + 1
        # Check naming convention (hyphen-case: lowercase with hyphens)
        if not re.match(r"^[a-z0-9-]+$", name):
            self.logger.log(
                LogLevel.ERROR,
                "invalid-name-format",
                f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)",
                file,
                line_number=line_number,
            )
            nb_errors += 1

        if name.startswith("-") or name.endswith("-") or "--" in name:
            self.logger.log(
                LogLevel.ERROR,
                "invalid-name-format",
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
                file,
                line_number=line_number,
            )
            nb_errors += 1

        # Check name length (max 64 characters per spec)
        if len(name) > self.MAX_NAME_LENGTH:
            self.logger.log(
                LogLevel.ERROR,
                "invalid-name-length",
                f"Name is too long ({len(name)}/{self.MAX_NAME_LENGTH} characters).",
                file,
                line_number=line_number,
            )
            nb_errors += 1

        # check if name matches directory name
        if name != file_path.name:
            self.logger.log(
                LogLevel.WARNING,
                "name-directory-mismatch",
                f"Name '{name}' does not match directory name '{file_path.name}'",
                file,
                line_number=line_number,
            )
            nb_warnings += 1

        return nb_warnings, nb_errors

    def validate_description(
        self, frontmatter: dict, file: str | Path, frontmatter_text: str, line_number: int = 1
    ) -> tuple[int, int]:
        """Validate the description field in frontmatter"""
        nb_warnings = 0
        nb_errors = 0
        if "description" not in frontmatter:
            self.logger.log(
                LogLevel.ERROR,
                "missing-description",
                "Missing 'description' in frontmatter",
                file,
                line_number=line_number,
            )
            return 0, 1

        line_number = self.parser.get_frontmatter_line_number(frontmatter_text, "description") + 1
        if frontmatter["description"] is None or not isinstance(frontmatter["description"], str):
            self.logger.log(
                LogLevel.ERROR,
                "invalid-description-type",
                f"Description must be a string, got {type(frontmatter['description']).__name__}",
                file,
                line_number=line_number,
            )
            return 0, 1

        description = frontmatter["description"].strip()
        if not description:
            self.logger.log(
                LogLevel.ERROR,
                "empty-description",
                "Description in frontmatter cannot be empty",
                file,
                line_number=line_number,
            )
            return 0, 1

        # Check for angle brackets
        if "<" in description or ">" in description:
            self.logger.log(
                LogLevel.ERROR,
                "invalid-description-format",
                "Description cannot contain angle brackets (< or >)",
                file,
                line_number=line_number,
            )
            nb_errors += 1

        # Check description length (max 1024 characters per spec)
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            self.logger.log(
                LogLevel.ERROR,
                "invalid-description-length",
                f"Description is too long ({len(description)}/{self.MAX_DESCRIPTION_LENGTH} characters).",
                file,
                line_number=line_number,
            )
            nb_errors += 1
        else:
            self.logger.log(
                LogLevel.INFO,
                "description-length",
                f"Description length: {len(description)}/{self.MAX_DESCRIPTION_LENGTH} characters.",
                file,
                line_number=line_number,
            )

        return nb_warnings, nb_errors
