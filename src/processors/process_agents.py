from pathlib import Path

from lib.config import Config
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from validators.agent_validator import AgentValidator


class ProcessAgents:
    def __init__(
        self,
        logger: Logger,
        parser: Parser,
        agent_validator: AgentValidator,
    ) -> None:
        self.logger = logger
        self.parser = parser
        self.agent_validator = agent_validator

    def process_agents(self, project_dir: Path, config: Config) -> tuple[int, int]:
        total_warnings = 0
        total_errors = 0
        # validate all AGENTS.md files in the project directory and subdirectories, excluding ignored directories
        self.logger.log(
            LogLevel.DEBUG,
            f"Validating AGENTS.md files in project directory: {project_dir} {config.ignore}",
        )

        agent_warnings, agent_errors = self.agent_validator.validate_agents_files(project_dir, config)
        total_warnings += agent_warnings
        total_errors += agent_errors

        return total_warnings, total_errors
