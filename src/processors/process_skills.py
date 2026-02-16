import fnmatch
import os
from pathlib import Path
from typing import Tuple

from lib.arguments import Arguments
from lib.config import Config
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from validators.skill_validator import SkillValidator


class ProcessSkills:
    def __init__(self, logger: Logger, parser: Parser, validator: SkillValidator) -> None:
        self.logger = logger
        self.parser = parser
        self.validator = validator

    def process_skill(self, skill_directory: Path, project_directory: Path, config: Config) -> Tuple[int, int]:
        # validate all skills in the skill directories
        total_warnings = 0
        total_errors = 0
        if skill_directory.is_dir():
            nb_warnings, nb_errors = self.validator.validate_skill(skill_directory, project_directory, config)
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

    def collect_skill_directories(
        self, directories: list[str], arguments: Arguments
    ) -> tuple[dict[str, str], set[str]]:
        """Collect skill directories from project directories.

        Returns:
            tuple: (skill_directories dict mapping skill_dir -> project_dir, project_dirs set)
        """
        skill_directories: dict[str, str] = {}
        project_dirs: set[str] = set()
        skills_count = 0

        for directory in directories:
            directory = os.path.abspath(directory)
            project_dirs.add(directory)

            if arguments.skills:
                # look for skills in .github/skills subdirectory
                skills_dir = os.path.abspath(f"{directory}/.github/skills")
                if os.path.exists(skills_dir) and os.path.isdir(skills_dir):
                    dirs = [
                        name
                        for name in os.listdir(skills_dir)
                        if os.path.isdir(os.path.join(skills_dir, name))
                        and os.path.exists(os.path.join(skills_dir, name, "SKILL.md"))
                    ]
                    for skill_dir in dirs:
                        full_skill_dir = os.path.join(skills_dir, skill_dir)
                        if full_skill_dir not in skill_directories:
                            skill_directories[full_skill_dir] = directory
                new_skills_count = len(skill_directories.keys())
                self.logger.log(
                    LogLevel.INFO,
                    f"Found {new_skills_count - skills_count} skills in directory '{directory}'",
                )
                skills_count = new_skills_count
                for skill_dir in skill_directories.keys():
                    if os.path.isdir(skill_dir):
                        project_dirs.add(str(self.validator.deduce_project_root_dir_from_skill_dir(skill_dir)))
            else:
                # add the directory if not already present
                if directory not in skill_directories:
                    project_dirs.add(directory)

        self.logger.log(
            LogLevel.INFO,
            f"Found {len(project_dirs)} unique project directories to process: {project_dirs} ",
        )

        return skill_directories, project_dirs

    def process_skills_for_directories(
        self, skill_directories: dict[str, str], config_loader: None, arguments: Arguments
    ) -> Tuple[int, int]:
        """Process all skills in the collected skill directories.

        Args:
            skill_directories: mapping of skill_dir -> project_dir
            config_loader: deprecated parameter (kept for compatibility), not used
            arguments: Arguments object with configuration overrides

        Returns:
            tuple: (total_warnings, total_errors)
        """
        total_warnings = 0
        total_errors = 0

        for skill_dir, project_dir in skill_directories.items():
            from lib.config import load_config

            config = load_config(self.logger, arguments, project_dir)
            # check if skill_dir should be ignored based on ignore patterns
            if any(fnmatch.fnmatch(str(skill_dir), str(pattern)) for pattern in config.ignore):
                self.logger.log(
                    LogLevel.INFO,
                    f"Skipping skill directory '{skill_dir}' as it matches ignore patterns",
                )
                continue
            self.logger.log(
                LogLevel.INFO,
                f"Processing skill directory: {skill_dir} (project: {project_dir})",
            )

            nb_warnings, nb_errors = self.process_skill(Path(skill_dir), Path(project_dir), config)
            total_warnings += nb_warnings
            total_errors += nb_errors

        return total_warnings, total_errors
