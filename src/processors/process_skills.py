from pathlib import Path
from typing import Tuple

from lib.log.logger import Logger, LogLevel
from lib.parser import Parser
from validators.skill_validator import SkillValidator


class ProcessSkills:
    def __init__(self, logger: Logger, parser: Parser, validator: SkillValidator) -> None:
        self.logger = logger
        self.parser = parser
        self.validator = validator

    def process_skill(self, skill_directory: Path, project_directory: Path) -> Tuple[int, int]:
        # validate all skills in the skill directories
        total_warnings = 0
        total_errors = 0
        if skill_directory.is_dir():
            nb_warnings, nb_errors = self.validator.validate_skill(skill_directory, project_directory)
            total_warnings += nb_warnings
            total_errors += nb_errors
        else:
            self.logger.logRule(
                LogLevel.ERROR,
                "directory-not-found",
                f"Skill directory '{skill_directory}' does not exist or is not a directory",
            )
            total_errors += 1

        return total_warnings, total_errors
