import re
from pathlib import Path
from typing import Sequence

from lib.config import Config
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from validators.code_snippet_validator import CodeSnippetValidator
from validators.content_length_validator import ContentLengthValidator
from validators.file_reference_validator import FileReferenceValidator


class AgentValidator:
    MAX_AGENT_CONTENT_TOKEN_COUNT = 5000  # Maximum allowed token count for skill content
    MAX_AGENT_CONTENT_LINES_COUNT = 500  # Maximum allowed lines in skill content
    # Compile regex patterns once for better performance
    # Matches markdown headers (# through ######) and captures the header text
    HEADER_PATTERN = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
    # Matches trailing hash symbols and whitespace in headers
    TRAILING_HASH_PATTERN = re.compile(r"\s*#+\s*$")

    def __init__(
        self,
        logger: Logger,
        parser: Parser,
        content_length_validator: ContentLengthValidator,
        file_reference_validator: FileReferenceValidator,
        code_snippet_validator: CodeSnippetValidator,
        config: Config,
    ):
        self.logger = logger
        self.parser = parser
        self.content_length_validator = content_length_validator
        self.file_reference_validator = file_reference_validator
        self.code_snippet_validator = code_snippet_validator
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

        line_number = frontmatter_text.count("\n") + 3 if frontmatter_text else 0
        desc_warnings, desc_errors = self.file_reference_validator.validate_content_file_references(
            base_dirs,
            agent_file,
            agent_content,
            line_number,
            project_dir=project_dir,
            resource_dirs=self.config.resource_dirs,
        )
        nb_warnings += desc_warnings
        nb_errors += desc_errors

        nb_warnings_content, nb_errors_content = self.content_length_validator.validate_content_length(
            agent_content,
            agent_file,
            line_number,
            self.MAX_AGENT_CONTENT_TOKEN_COUNT,
            self.MAX_AGENT_CONTENT_LINES_COUNT,
            project_dir=project_dir,
            file_type="Agent",
            warning_threshold=self.config.report_warning_threshold,
        )
        nb_warnings += nb_warnings_content
        nb_errors += nb_errors_content

        snippet_warnings, snippet_errors = self.code_snippet_validator.validate_code_snippets(
            agent_file, project_dir, agent_content, line_number
        )
        nb_warnings += snippet_warnings
        nb_errors += snippet_errors

        # Section validation
        section_warnings, section_errors = self._validate_sections(agent_content, agent_file, project_dir)
        nb_warnings += section_warnings
        nb_errors += section_errors

        return nb_warnings, nb_errors

    def validate_agents_files(self, project_dir: Path, ignore_dirs: Sequence[Path] | None) -> tuple[int, int]:
        """Validate all AGENTS.md files in the project directory"""
        project_dir = Path(project_dir)
        agent_files = list(project_dir.rglob("AGENTS.md"))
        nb_warnings = 0
        nb_errors = 0
        if not agent_files:
            level = self.config.missing_agents_file_level
            self.logger.logRule(
                level,
                "no-agents-found",
                "No AGENTS.md file found in the project directory",
                project_dir,
            )
            if level == LogLevel.ERROR:
                nb_errors += 1
            elif level == LogLevel.WARNING:
                nb_warnings += 1

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

    def _extract_sections(self, content: str) -> list[str]:
        """Extract section titles from markdown content

        Args:
            content: The markdown content to parse

        Returns:
            List of section titles (normalized to lowercase)
        """
        sections = []
        # Use pre-compiled pattern for better performance
        matches = self.HEADER_PATTERN.findall(content)

        for match in matches:
            # Remove markdown formatting and normalize
            section_title = match.strip()
            # Remove trailing hash symbols and whitespace using pre-compiled pattern
            section_title = self.TRAILING_HASH_PATTERN.sub("", section_title)
            # Normalize to lowercase for case-insensitive comparison
            sections.append(section_title.lower())

        return sections

    def _validate_sections(self, content: str, agent_file: Path, project_dir: Path) -> tuple[int, int]:
        """Validate that agent content contains required sections

        Args:
            content: The agent content to validate
            agent_file: Path to the agent file
            project_dir: Project root directory

        Returns:
            Tuple of (warnings, errors) counts
        """
        nb_warnings = 0
        nb_errors = 0

        # Extract sections from content
        found_sections = self._extract_sections(content)

        # Check mandatory sections
        if self.config.enable_section_mandatory:
            for mandatory_section in self.config.mandatory_sections:
                mandatory_lower = mandatory_section.lower()
                if mandatory_lower not in found_sections:
                    level = self.config.missing_section_level
                    self.logger.logRule(
                        level,
                        "missing-mandatory-section",
                        f'Missing mandatory section: "{mandatory_section}"',
                        agent_file.relative_to(project_dir),
                    )
                    if level == LogLevel.ERROR:
                        nb_errors += 1
                    elif level == LogLevel.WARNING:
                        nb_warnings += 1

        # Check recommended sections (only if advices are enabled)
        if self.config.enable_section_advices:
            for recommended_section in self.config.recommended_sections:
                recommended_lower = recommended_section.lower()
                if recommended_lower not in found_sections:
                    self.logger.logRule(
                        LogLevel.ADVICE,
                        "missing-recommended-section",
                        f'Consider adding recommended section: "{recommended_section}"',
                        agent_file.relative_to(project_dir),
                    )
                    # Advices don't count as warnings or errors

        return nb_warnings, nb_errors
