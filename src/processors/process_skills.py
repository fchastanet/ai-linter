import os
from typing import List, Tuple

from lib.log import Logger, LogLevel
from lib.parser import Parser
from validators.skill_validator import SkillValidator


class ProcessSkills:
    def __init__(self, logger: Logger, parser: Parser, validator: SkillValidator) -> None:
        self.logger = logger
        self.parser = parser
        self.validator = validator

    def process_skills(self, skill_directories: List[str]) -> Tuple[int, int]:
        # validate all skills in the skill directories
        total_warnings = 0
        total_errors = 0
        for skill_dir in skill_directories:
            if os.path.isdir(skill_dir):
                nb_warnings, nb_errors = self.validator.validate_skill(skill_dir)
                total_warnings += nb_warnings
                total_errors += nb_errors
            else:
                self.logger.log(
                    LogLevel.ERROR,
                    "directory-not-found",
                    f"Skill directory '{skill_dir}' does not exist or is not a directory",
                )
                total_errors += 1

        return total_warnings, total_errors
