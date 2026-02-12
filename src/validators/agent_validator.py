import re
from pathlib import Path
from typing import Sequence

import pathspec

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
    ):
        self.logger = logger
        self.parser = parser
        self.content_length_validator = content_length_validator
        self.file_reference_validator = file_reference_validator
        self.code_snippet_validator = code_snippet_validator

    def validate_agent_file(
        self, base_dirs: Sequence[Path], agent_file: Path, project_dir: Path, config: Config
    ) -> tuple[int, int]:
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
            resource_dirs=config.resource_dirs,
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
            warning_threshold=config.report_warning_threshold,
        )
        nb_warnings += nb_warnings_content
        nb_errors += nb_errors_content

        snippet_warnings, snippet_errors = self.code_snippet_validator.validate_code_snippets(
            agent_file, project_dir, agent_content, line_number
        )
        nb_warnings += snippet_warnings
        nb_errors += snippet_errors

        # Section validation
        section_warnings, section_errors = self._validate_sections(agent_content, agent_file, project_dir, config)
        nb_warnings += section_warnings
        nb_errors += section_errors

        return nb_warnings, nb_errors

    def validate_agents_files(self, project_dir: Path, config: Config) -> tuple[int, int]:
        """Validate all AGENTS.md files in the project directory"""
        project_dir = Path(project_dir)
        agent_files = list(project_dir.rglob("AGENTS.md"))
        # remove files with non case-sensitive match
        agent_files = [f for f in agent_files if f.name == "AGENTS.md"]
        nb_warnings = 0
        nb_errors = 0
        if not agent_files:
            level = config.missing_agents_file_level
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

        # Create a pathspec from ignore patterns
        spec = pathspec.PathSpec.from_lines("gitwildmatch", config.ignore)

        # Filter files: keep only those that DON'T match any ignore pattern
        filtered_agent_files = [f for f in agent_files if not spec.match_file(str(f.relative_to(project_dir)))]

        if len(filtered_agent_files) < len(agent_files):
            ignored_files = set(agent_files) - set(filtered_agent_files)
            self.logger.log(
                LogLevel.DEBUG,
                f"Skipping AGENTS.md file as it matches ignore patterns for {ignored_files}",
            )
        self.logger.log(
            LogLevel.INFO,
            f"Found {len(filtered_agent_files)} AGENTS.md file(s) to validate after applying ignore patterns",
        )
        for agent_file in filtered_agent_files:
            self.logger.log(
                LogLevel.INFO,
                f"Validating AGENTS.md file: {agent_file}",
            )
            agent_warnings, agent_errors = self.validate_agent_file(
                [agent_file.parent, project_dir], agent_file, project_dir, config=config
            )
            nb_warnings += agent_warnings
            nb_errors += agent_errors

        return nb_warnings, nb_errors

    def _extract_sections(self, content: str) -> dict[str, str]:
        """Extract section titles from markdown content

        Args:
            content: The markdown content to parse

        Returns:
            A dictionary mapping normalized (lowercased) section titles to their original titles.
        """
        sections = dict()
        # Use pre-compiled pattern for better performance
        matches = self.HEADER_PATTERN.findall(content)

        for match in matches:
            # Remove markdown formatting and normalize
            section_title = match.strip()
            # Remove trailing hash symbols and whitespace using pre-compiled pattern
            section_title = self.TRAILING_HASH_PATTERN.sub("", section_title)
            # Normalize to lowercase for case-insensitive comparison
            sections[section_title.lower()] = section_title

        return sections

    def _validate_sections(self, content: str, agent_file: Path, project_dir: Path, config: Config) -> tuple[int, int]:
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
        if config.enable_mandatory_sections:
            for mandatory_section_key, mandatory_section_label in config.mandatory_sections.items():
                if mandatory_section_key not in found_sections:
                    level = config.mandatory_sections_log_level
                    self.logger.logRule(
                        level,
                        "missing-mandatory-section",
                        f'Missing mandatory section: "{mandatory_section_label}"',
                        agent_file.relative_to(project_dir),
                    )
                    if level == LogLevel.ERROR:
                        nb_errors += 1
                    elif level == LogLevel.WARNING:
                        nb_warnings += 1

        # Check advised sections (only if advised sections are enabled)
        if config.enable_advised_sections:
            for advised_section_key, advised_section_label in config.advised_sections.items():
                if advised_section_key not in found_sections:
                    self.logger.logRule(
                        LogLevel.ADVICE,
                        "missing-advised-section",
                        f'Consider adding advised section: "{advised_section_label}"',
                        agent_file.relative_to(project_dir),
                    )
                    # Advised sections don't count as warnings or errors

        return nb_warnings, nb_errors
