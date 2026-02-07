from pathlib import Path
from typing import Sequence

from lib.config import Config
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from validators.code_snippet_validator import CodeSnippetValidator
from validators.file_reference_validator import FileReferenceValidator
from validators.unreferenced_file_validator import UnreferencedFileValidator


class AgentValidator:
    MAX_AGENT_CONTENT_TOKEN_COUNT = 5000  # Maximum allowed token count for skill content
    MAX_AGENT_CONTENT_LINES_COUNT = 500  # Maximum allowed lines in skill content

    def __init__(
        self,
        logger: Logger,
        parser: Parser,
        file_reference_validator: FileReferenceValidator,
        code_snippet_validator: CodeSnippetValidator,
        unreferenced_file_validator: UnreferencedFileValidator,
        config: Config,
    ):
        self.logger = logger
        self.parser = parser
        self.file_reference_validator = file_reference_validator
        self.code_snippet_validator = code_snippet_validator
        self.unreferenced_file_validator = unreferenced_file_validator
        self.config = config

    def validate_agent_file(self, base_dirs: Sequence[Path], agent_file: Path, project_dir: Path) -> tuple[int, int]:
        """Validate a single AGENTS.md file"""
        nb_errors = 0
        nb_warnings = 0
        # frontmatter validation
        frontmatter_text, agent_content = self.parser.parse_content_and_frontmatter(agent_file, False)
        if frontmatter_text is not None:
            self.logger.logRule(
                LogLevel.ERROR,
                "agent-frontmatter-extracted",
                "AGENTS.md should not contain frontmatter",
                agent_file.relative_to(project_dir),
            )
            nb_errors += 1

        if agent_content is None:
            self.logger.logRule(
                LogLevel.ERROR,
                "agent-content-missing",
                "AGENTS.md content is missing",
                agent_file.relative_to(project_dir),
            )
            nb_errors += 1
            return nb_warnings, nb_errors

        line_number = frontmatter_text.count("\n") + 3 if frontmatter_text else 1
        desc_warnings, desc_errors = self.file_reference_validator.validate_content_file_references(
            base_dirs, agent_file, agent_content, line_number, project_dir=project_dir
        )
        nb_warnings += desc_warnings
        nb_errors += desc_errors

        nb_warnings_content, nb_errors_content = self.file_reference_validator.validate_content_length(
            agent_content,
            agent_file,
            line_number,
            self.MAX_AGENT_CONTENT_TOKEN_COUNT,
            self.MAX_AGENT_CONTENT_LINES_COUNT,
            project_dir=project_dir,
        )
        nb_warnings += nb_warnings_content
        nb_errors += nb_errors_content

        snippet_warnings, snippet_errors = self.code_snippet_validator.validate_code_snippets(
            agent_file, project_dir, agent_content
        )
        nb_warnings += snippet_warnings
        nb_errors += snippet_errors

        # Validate unreferenced files in resource directories
        # Pass the agent content directly to avoid re-reading the file
        full_content = frontmatter_text + "\n---\n" + agent_content if frontmatter_text else agent_content
        unref_warnings, unref_errors = self.unreferenced_file_validator.validate_unreferenced_files(
            project_dir=agent_file.parent,
            relative_to=project_dir,
            resource_dirs=[Path(d) for d in self.config.resource_dirs],
            markdown_content=full_content,
            markdown_file=agent_file,
            ignore_dirs=[Path(d) for d in self.config.ignore_dirs],
            level=self.config.unreferenced_file_level,
        )
        nb_warnings += unref_warnings
        nb_errors += unref_errors

        return nb_warnings, nb_errors

    def validate_agents_files(self, project_dir: Path, ignore_dirs: Sequence[Path] | None) -> tuple[int, int]:
        """Validate all AGENTS.md files in the project directory"""
        project_dir = Path(project_dir)
        agent_files = list(project_dir.rglob("AGENTS.md"))
        nb_warnings = 0
        nb_errors = 0
        for agent_file in agent_files:
            if ignore_dirs is not None and any(str(ignored_dir) in str(agent_file) for ignored_dir in ignore_dirs):
                self.logger.logRule(
                    LogLevel.DEBUG,
                    "ignoring-agents-file",
                    f"Ignoring AGENTS.md file due to ignore_dirs setting: {ignore_dirs}",
                    agent_file.relative_to(project_dir),
                )
                continue
            self.logger.log(LogLevel.INFO, "Validating AGENTS.md file: %s", (str(agent_file.relative_to(project_dir)),))
            agent_warnings, agent_errors = self.validate_agent_file(
                [agent_file.parent, project_dir], agent_file, project_dir
            )
            nb_warnings += agent_warnings
            nb_errors += agent_errors
        return nb_warnings, nb_errors
