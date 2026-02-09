"""Processor for validating prompt and agent markdown files"""

from pathlib import Path
from typing import Sequence

from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from validators.content_length_validator import ContentLengthValidator
from validators.file_reference_validator import FileReferenceValidator


class ProcessPrompts:
    """Process and validate prompt/agent markdown files in specified directories"""

    def __init__(
        self,
        logger: Logger,
        parser: Parser,
        content_length_validator: ContentLengthValidator,
        file_reference_validator: FileReferenceValidator,
    ):
        self.logger = logger
        self.parser = parser
        self.content_length_validator = content_length_validator
        self.file_reference_validator = file_reference_validator

    def process_markdown_file(
        self,
        file_path: Path,
        project_dir: Path,
        max_tokens: int,
        max_lines: int,
        file_type: str,
        warning_threshold: float,
    ) -> tuple[int, int]:
        """Process a single markdown file for validation.

        Args:
            file_path: Path to the markdown file
            project_dir: Project root directory
            max_tokens: Maximum allowed tokens
            max_lines: Maximum allowed lines
            file_type: Type of file ("Prompt" or "Agent")
            warning_threshold: Threshold for warning status

        Returns:
            Tuple of (warnings, errors)
        """
        nb_warnings = 0
        nb_errors = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Validate content length
            nb_warnings_content, nb_errors_content = self.content_length_validator.validate_content_length(
                content,
                file_path,
                1,
                max_tokens,
                max_lines,
                project_dir=project_dir,
                file_type=file_type,
                warning_threshold=warning_threshold,
            )
            nb_warnings += nb_warnings_content
            nb_errors += nb_errors_content

            # Validate file references
            nb_warnings_ref, nb_errors_ref = self.file_reference_validator.validate_content_file_references(
                [file_path, project_dir],
                file_path,
                content,
                1,
                project_dir=project_dir,
                resource_dirs=[],  # Prompts/Agents shouldn't reference resource files
            )
            nb_warnings += nb_warnings_ref
            nb_errors += nb_errors_ref

        except Exception as e:
            self.logger.logRule(
                LogLevel.ERROR,
                "file-read-error",
                f"Failed to read file: {e}",
                file=file_path,
            )
            nb_errors += 1

        return nb_warnings, nb_errors

    def process_sub_directories(
        self,
        project_dirs: Sequence[Path],
        sub_dirs: list[str],
        file_type: str,
        max_tokens: int,
        max_lines: int,
        warning_threshold: float,
        ignore_dirs: Sequence[Path] | None = None,
    ) -> tuple[int, int]:
        """Process all markdown files in directories (excluding AGENTS.md/SKILL.md).

        Args:
            project_dirs: Project root directories to search
            sub_dirs: List of directory patterns (e.g., [".github/agents", ".github/prompts"])
            max_tokens: Maximum allowed tokens
            max_lines: Maximum allowed lines
            warning_threshold: Threshold for warning status
            ignore_dirs: Directories to ignore

        Returns:
            Tuple of (total_warnings, total_errors)
        """
        nb_warnings = 0
        nb_errors = 0

        for project_dir in project_dirs:
            for sub_dir_pattern in sub_dirs:
                sub_dir = project_dir / sub_dir_pattern
                if not sub_dir.exists() or not sub_dir.is_dir():
                    continue

                # Find all markdown files except AGENTS.md and SKILL.md
                md_files = [f for f in sub_dir.rglob("*.md") if f.name != "AGENTS.md" and f.name != "SKILL.md"]

                if md_files:
                    self.logger.log(
                        LogLevel.INFO,
                        f"Found {len(md_files)} {file_type} file(s) in {sub_dir}",
                    )

                for md_file in md_files:
                    # Skip ignored directories
                    if ignore_dirs:
                        skip = False
                        for ignore_dir in ignore_dirs:
                            if ignore_dir in md_file.parents:
                                skip = True
                                break
                        if skip:
                            continue

                    self.logger.log(
                        LogLevel.INFO,
                        f"Processing {file_type} file: {md_file}",
                    )

                    file_warnings, file_errors = self.process_markdown_file(
                        md_file,
                        project_dir,
                        max_tokens,
                        max_lines,
                        file_type,
                        warning_threshold,
                    )
                    nb_warnings += file_warnings
                    nb_errors += file_errors

        return nb_warnings, nb_errors
