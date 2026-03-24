import re
from collections.abc import Sequence
from pathlib import Path

from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser


class FileReferenceValidator:

    def __init__(self, logger: Logger, parser: Parser):
        self.logger = logger
        self.parser = parser

    def validate_content_file_references(
        self,
        base_dirs: Sequence[Path],
        file: Path,
        content: str,
        content_start_line_number: int,
        project_dir: Path,
        resource_dirs: Sequence[str],
    ) -> tuple[int, int]:
        """Parse content to extract file links (if any)"""
        file_links: dict[str, int] = self._extract_file_references(content)
        file_error_count = 0
        file_warning_count = 0
        new_file_links = file_links.copy()
        for link, line_number in file_links.items():
            self.logger.log(LogLevel.DEBUG, f"Validating file link: {link}")
            relative_link = self._validate_file_link(base_dirs, file, link)
            if isinstance(relative_link, str):
                new_file_links[relative_link] = line_number
            else:
                self.logger.logRule(
                    LogLevel.ERROR,
                    "file-link-not-found",
                    f"File link '{link}' not found in any of the base directories: {base_dirs}",
                    file=file.relative_to(project_dir),
                    line_number=content_start_line_number + line_number,
                )
                file_error_count += 1

        unreferenced_warnings, unreferenced_errors = self._validate_all_resource_files_are_referenced(
            file, content_start_line_number, project_dir, resource_dirs, new_file_links
        )
        file_warning_count += unreferenced_warnings
        file_error_count += unreferenced_errors

        return file_warning_count, file_error_count

    def _validate_all_resource_files_are_referenced(
        self,
        file: Path,
        content_start_line_number: int,
        project_dir: Path,
        resource_dirs: Sequence[str],
        file_links: dict[str, int],
    ) -> tuple[int, int]:
        """
        Validate that all files in resource directories just under the content directory are referenced
        in the content
        Args:
            base_dirs: Base directories containing resource files (e.g., content directory and specified
                resource directories)
            file: The markdown file being validated
            content: The content without frontmatter to check for references
            content_start_line_number: Line number where content starts
            project_dir: Project directory for relative path resolution
            file_links: Dictionary of file links already found in the content with their line numbers
                (to avoid duplicates)
        """
        # This method can be used to check for unreferenced files in resource directories, which might
        # indicate leftover or mistakenly added files.
        # We only check for files that are in the same directory as the markdown file under specified
        # resource directories, to avoid false positives on unrelated files
        content_dir = file.parent
        warning_count = 0
        error_count = 0
        for resource_dir in resource_dirs:
            resource_path = content_dir / resource_dir
            if resource_path.exists() and resource_path.is_dir():
                for file_path in resource_path.rglob("*"):
                    if file_path.is_file():
                        try:
                            relative_to_content = file_path.relative_to(content_dir)
                            relative_str = str(relative_to_content).replace("\\", "/")
                            if relative_str not in file_links:
                                self.logger.logRule(
                                    LogLevel.WARNING,
                                    "unreferenced-file-link",
                                    f"File '{relative_str}' in resource directory is not referenced in the content",
                                    file=file.relative_to(project_dir),
                                    line_number=content_start_line_number,
                                )
                                warning_count += 1
                        except ValueError:
                            # File is outside content directory, skip
                            pass

        return warning_count, error_count

    def _extract_file_references(self, content: str) -> dict[str, int]:
        """
        Extract all file references from markdown content.
        Looks for:
        - Markdown links: [text](path/to/file)
        - HTML img tags: <img src="path/to/file">
        - Attachment references: <attachment filePath="path/to/file">
        """
        references: dict[str, int] = {}

        # Markdown links and images: [text](path) or ![alt](path)
        link_pattern = r"!?\[([^\]]*)\]\((?P<link>[^)]+)\)"
        for m, line_number in self.parser.finditer_with_line_numbers(link_pattern, content):
            ref = m.group("link")
            self._add_file_reference_if_seems_valid(ref, line_number, references)

        # HTML img/src tags: <img src="path">
        img_pattern = r'<img[^>]+src=["\'](?P<link>[^"\']+)["\']'
        for m, line_number in self.parser.finditer_with_line_numbers(img_pattern, content):
            ref = m.group("link")
            self._add_file_reference_if_seems_valid(ref, line_number, references)

        # Attachment references: <attachment filePath="path">
        attachment_pattern = r'<attachment[^>]+filePath=["\'](?P<link>[^"\']+)["\']'
        for m, line_number in self.parser.finditer_with_line_numbers(attachment_pattern, content):
            ref = m.group("link")
            self._add_file_reference_if_seems_valid(ref, line_number, references)

        # AGENTS.md file style references: `@./filepath` or `@/filepath`
        agent_ref_pattern = r"`@(?P<link>\.?/[^`\n]+)`"
        for m, line_number in self.parser.finditer_with_line_numbers(agent_ref_pattern, content):
            ref = m.group("link")
            self._add_file_reference_if_seems_valid(ref, line_number, references)

        return references

    def _add_file_reference_if_seems_valid(self, link: str, line_number: int, references: dict[str, int]) -> None:
        """
        Add a file reference to the dictionary if it seems valid
        (contains / and no spaces, quotes, *, ?, tab or newlines)
        """
        if link in references:
            return
        self.logger.log(LogLevel.DEBUG, f"Found file link: {link}")
        # check if it seems like a file path (i.e., contains at least one /)
        # Regex: at least one /, and no * or ? or space
        # @see https://regex101.com/r/gRA5Sy/4
        if re.search(r"^(?=[^*?]*\/)[^\t\n *?\\<>$|:\"'`]+$", link):
            references[link] = line_number
        else:
            self.logger.log(
                LogLevel.DEBUG,
                f"Ignoring link that doesn't look like a file path: {link}",
            )

    def _validate_file_link(
        self,
        base_dirs: Sequence[Path],
        file: Path,
        link: str,
    ) -> str | bool:
        """
        Validate that a file link exists relative to base directories
        Returns the relative link if valid, False if not valid
        """
        # make link relative to content directory for unreferenced file validation
        relative_link: str | bool = False
        # remove leading ./ if present
        if link.startswith("./"):
            link = link[2:]
        # remove leading / if present to avoid absolute path issues
        if link.startswith("/"):
            link = link[1:]
        # check first if relative to the markdown file, then try to make it relative
        # to each base dir (e.g., content dir) if not already relative
        try:
            full_path = Path.resolve(file.parent / link)
            if full_path.exists():
                relative_link = str(full_path).replace("\\", "/")
        except ValueError:
            pass

        if not relative_link:
            for base_dir in base_dirs:
                try:
                    full_path = Path.resolve(base_dir / link)
                    if full_path.exists():
                        relative_link = str(full_path).replace("\\", "/")
                        break
                except ValueError:
                    continue

        return relative_link
