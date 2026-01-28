from pathlib import Path

from pyparsing import Sequence

from lib.log import Logger, LogLevel
from lib.parser import Parser
from validators.file_reference_validator import FileReferenceValidator


class AgentValidator:
    MAX_AGENT_CONTENT_TOKEN_COUNT = 5000  # Maximum allowed token count for skill content
    MAX_AGENT_CONTENT_LINES_COUNT = 500  # Maximum allowed lines in skill content

    def __init__(
        self,
        logger: Logger,
        parser: Parser,
        file_reference_validator: FileReferenceValidator,
    ):
        self.logger = logger
        self.parser = parser
        self.file_reference_validator = file_reference_validator

    def validate_agent_file(self, base_dirs: Sequence[str | Path], agent_file: Path) -> tuple[int, int]:
        """Validate a single AGENTS.md file"""
        nb_errors = 0
        nb_warnings = 0
        # frontmatter validation
        frontmatter_text, agent_content = self.parser.parse_content_and_frontmatter(agent_file, False)
        if frontmatter_text is not None:
            self.logger.log(
                LogLevel.ERROR,
                "agent-frontmatter-extracted",
                "AGENTS.md should not contain frontmatter",
                agent_file,
            )
            nb_errors += 1

        if agent_content is None:
            self.logger.log(
                LogLevel.ERROR,
                "agent-content-missing",
                "AGENTS.md content is missing",
                agent_file,
            )
            nb_errors += 1
            return nb_warnings, nb_errors

        line_number = frontmatter_text.count("\n") + 3 if frontmatter_text else 1
        desc_warnings, desc_errors = self.file_reference_validator.validate_content_file_references(
            base_dirs, agent_file, agent_content, line_number
        )
        nb_warnings += desc_warnings
        nb_errors += desc_errors

        nb_warnings_content, nb_errors_content = self.file_reference_validator.validate_content_length(
            agent_content,
            agent_file,
            line_number,
            self.MAX_AGENT_CONTENT_TOKEN_COUNT,
            self.MAX_AGENT_CONTENT_LINES_COUNT,
        )
        nb_warnings += nb_warnings_content
        nb_errors += nb_errors_content

        return nb_warnings, nb_errors

    def validate_agents_files(self, project_dir: str | Path, ignore_dirs: Sequence[str | Path] = []) -> tuple[int, int]:
        """Validate all AGENTS.md files in the project directory"""
        project_dir = Path(project_dir)
        agent_files = list(project_dir.rglob("AGENTS.md"))
        nb_warnings = 0
        nb_errors = 0
        for agent_file in agent_files:
            if any(str(ignored_dir) in str(agent_file) for ignored_dir in ignore_dirs):
                self.logger.log(
                    LogLevel.DEBUG,
                    "ignoring-agents-file",
                    f"Ignoring AGENTS.md file due to ignore_dirs setting: {ignore_dirs}",
                    agent_file,
                )
                continue
            self.logger.log(
                LogLevel.INFO,
                "validating-agents-file",
                f"Validating AGENTS.md file: {agent_file}",
                agent_file,
            )
            agent_warnings, agent_errors = self.validate_agent_file([agent_file.parent, project_dir], agent_file)
            nb_warnings += agent_warnings
            nb_errors += agent_errors
        return nb_warnings, nb_errors
