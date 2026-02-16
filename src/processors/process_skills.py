import os
from pathlib import Path

from filters.filter_files import is_ignored_path
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

    def process_skill(self, skill_directory: Path, project_directory: Path, config: Config) -> tuple[int, int]:
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
            project_dir = os.path.abspath(directory)
            project_dirs.add(project_dir)
            from lib.config import load_config

            config = load_config(self.logger, arguments, project_dir)

            if arguments.skills:
                # look for skills in .github/skills subdirectory
                skills_dir = os.path.abspath(f"{project_dir}/.github/skills")
                if os.path.exists(skills_dir) and os.path.isdir(skills_dir):
                    dirs = [
                        name
                        for name in os.listdir(skills_dir)
                        if os.path.isdir(os.path.join(skills_dir, name))
                        and os.path.exists(os.path.join(skills_dir, name, "SKILL.md"))
                    ]
                    for skill_dir in dirs:
                        full_skill_dir = os.path.join(skills_dir, skill_dir)
                        if full_skill_dir not in skill_directories and not is_ignored_path(
                            self.logger, config.ignore, Path(full_skill_dir).relative_to(project_dir)
                        ):
                            skill_directories[full_skill_dir] = project_dir
                new_skills_count = len(skill_directories.keys())
                self.logger.log(
                    LogLevel.INFO,
                    "Found %d skills in directory '%s'",
                    new_skills_count - skills_count,
                    project_dir,
                )
                skills_count = new_skills_count
                for skill_dir in skill_directories.keys():
                    if os.path.isdir(skill_dir):
                        project_dirs.add(str(self.validator.deduce_project_root_dir_from_skill_dir(skill_dir)))
            else:
                # add the directory if not already present
                if project_dir not in skill_directories:
                    project_dirs.add(project_dir)

        self.logger.log(
            LogLevel.INFO,
            "Found %d unique project directories to process: %s",
            len(project_dirs),
            project_dirs,
        )

        return skill_directories, project_dirs

    def process_skills_for_directories(
        self, skill_directories: dict[str, str], arguments: Arguments
    ) -> tuple[int, int]:
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
            # check if skill_dir should be ignored based on ignore patterns
            skill_path = Path(skill_dir)
            project_path = Path(project_dir)
            relative_path = skill_path.relative_to(project_path).as_posix()
            self.logger.log(
                LogLevel.INFO,
                "Processing skill directory: %s (project: %s)",
                relative_path,
                project_dir,
            )

            # Load config for the project directory
            from lib.config import load_config

            config = load_config(self.logger, arguments, project_dir)

            # Process the skill directory
            nb_warnings, nb_errors = self.process_skill(Path(skill_dir), Path(project_dir), config)
            total_warnings += nb_warnings
            total_errors += nb_errors

        return total_warnings, total_errors
