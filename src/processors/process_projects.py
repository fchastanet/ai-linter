from pathlib import Path

from filters.filter_files import is_ignored_path
from lib.arguments import Arguments
from lib.config import load_config
from lib.log.logger import Logger
from lib.parser import Parser
from processors.process_agents import ProcessAgents
from processors.process_prompts import ProcessPrompts


class ProcessProjects:
    """Handles processing of project directories for agents, prompts, and agent configurations"""

    def __init__(
        self,
        logger: Logger,
        parser: Parser,
        process_agents: ProcessAgents,
        process_prompts: ProcessPrompts,
    ) -> None:
        self.logger = logger
        self.parser = parser
        self.process_agents = process_agents
        self.process_prompts = process_prompts

    def process_projects_for_directories(self, project_dirs: set[str], arguments: Arguments) -> tuple[int, int]:
        """Process all projects in the given directories.

        Validates:
        - AGENTS.md files for agent configurations
        - Prompts in .github/prompts directories
        - Agents in .github/agents directories

        Args:
            project_dirs: Set of project directory paths to process
            arguments: Arguments object with configuration overrides

        Returns:
            tuple: (total_warnings, total_errors)
        """
        total_warnings = 0
        total_errors = 0

        for project_dir in project_dirs:
            config = load_config(self.logger, arguments, project_dir)
            if is_ignored_path(self.logger, config.ignore, Path(project_dir)):
                continue
            project_path = Path(project_dir)

            # Process agents in AGENTS.md files
            nb_warnings, nb_errors = self.process_agents.process_agents(project_path, config)
            total_warnings += nb_warnings
            total_errors += nb_errors

            # Process prompts in .github/prompts directories
            nb_warnings, nb_errors = self.process_prompts.process_sub_directories(
                project_path,
                config.ignore,
                "Prompt",
                config.prompt_dirs,
                config.prompt_max_tokens,
                config.prompt_max_lines,
                config.report_warning_threshold,
            )
            total_warnings += nb_warnings
            total_errors += nb_errors

            # Process agents in .github/agents directories (excluding AGENTS.md)
            nb_warnings, nb_errors = self.process_prompts.process_sub_directories(
                project_path,
                config.ignore,
                "Agent",
                config.agent_dirs,
                config.agent_max_tokens,
                config.agent_max_lines,
                config.report_warning_threshold,
            )
            total_warnings += nb_warnings
            total_errors += nb_errors

        return total_warnings, total_errors
