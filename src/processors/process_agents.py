import fnmatch
from pathlib import Path
from typing import Sequence, Tuple

from lib.log import Logger, LogLevel
from lib.parser import Parser
from validators.agent_validator import AgentValidator


class ProcessAgents:
    def __init__(self, logger: Logger, parser: Parser, agent_validator: AgentValidator) -> None:
        self.logger = logger
        self.parser = parser
        self.agent_validator = agent_validator

    def process_agents(
        self, project_dirs: Sequence[str | Path], ignore_dirs: Sequence[str | Path] = []
    ) -> Tuple[int, int]:
        if ignore_dirs is None:
            ignore_dirs = []
        total_warnings = 0
        total_errors = 0
        # validate all AGENTS.md files in the project directories
        for project_dir in project_dirs:
            # check if project dir is one of the ignore directories
            self.logger.log(
                LogLevel.DEBUG,
                "validating-agents-in-project-dir",
                f"Validating AGENTS.md files in project directory: {project_dir} {ignore_dirs}",
            )

            # check if project dir matches any ignore_dirs glob pattern
            if any(fnmatch.fnmatch(str(project_dir), str(pattern)) for pattern in ignore_dirs):
                self.logger.log(
                    LogLevel.DEBUG,
                    "ignoring-project-dir",
                    f"Ignoring project directory '{project_dir}' due to ignore_dirs setting: {ignore_dirs}",
                )
                continue

            agent_warnings, agent_errors = self.agent_validator.validate_agents_files(project_dir, ignore_dirs)
            total_warnings += agent_warnings
            total_errors += agent_errors

        return total_warnings, total_errors
