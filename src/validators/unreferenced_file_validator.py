import re
from pathlib import Path

from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class UnreferencedFileValidator:
    """Validator to check that all files in resource directories are referenced in .md files"""

    def __init__(self, logger: Logger):
        self.logger = logger

    def find_all_markdown_files(self, directory: str | Path, ignore_dirs: list[Path] | None = None) -> list[Path]:
        """Find all markdown files in a directory"""
        directory = Path(directory)
        if ignore_dirs is None:
            ignore_dirs = []

        # Compare directory names (strings) instead of Path objects against md_file.parts
        ignore_dir_names = {ignored.name for ignored in ignore_dirs}
        markdown_files = []
        for md_file in directory.rglob("*.md"):
            # Skip ignored directories
            if any(ignored_name in md_file.parts for ignored_name in ignore_dir_names):
                continue
            markdown_files.append(md_file)

        return markdown_files

    def extract_file_references(self, markdown_content: str) -> set[str]:
        """
        Extract all file references from markdown content
        Looks for:
        - Markdown links: [text](path/to/file)
        - HTML img tags: <img src="path/to/file">
        - Attachment references: <attachment filePath="path/to/file">
        - Relative file paths in various formats
        """
        references = set()

        # Markdown links and images: [text](path) or ![alt](path)
        link_pattern = r"!?\[([^\]]*)\]\(([^)]+)\)"
        for match in re.finditer(link_pattern, markdown_content):
            ref = match.group(2)
            # Remove URL anchors and query strings
            ref = ref.split("#")[0].split("?")[0]
            if ref and not ref.startswith(("http://", "https://", "mailto:", "#")):
                references.add(ref)

        # HTML img/src tags: <img src="path">
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        for match in re.finditer(img_pattern, markdown_content):
            ref = match.group(1)
            if ref and not ref.startswith(("http://", "https://", "data:")):
                references.add(ref)

        # Attachment references: <attachment filePath="path">
        attachment_pattern = r'<attachment[^>]+filePath=["\']([^"\']+)["\']'
        for match in re.finditer(attachment_pattern, markdown_content):
            references.add(match.group(1))

        # Code blocks with file references (e.g., source: path/to/file)
        code_ref_pattern = r"(?:source|file|path):\s*([^\s\n]+)"
        for match in re.finditer(code_ref_pattern, markdown_content, re.IGNORECASE):
            ref = match.group(1)
            if ref and not ref.startswith(("http://", "https://")):
                references.add(ref)

        return references

    def get_all_references_in_directory(
        self, directory: Path, ignore_dirs: list[Path] | None = None
    ) -> dict[str, set[str]]:
        """
        Get all file references from all markdown files in a directory
        Returns a dict mapping file paths to sets of references
        """
        markdown_files = self.find_all_markdown_files(directory, ignore_dirs)
        all_references = {}

        for md_file in markdown_files:
            try:
                content = md_file.read_text()
                refs = self.extract_file_references(content)
                if refs:
                    all_references[str(md_file)] = refs
            except Exception as e:
                self.logger.logRule(
                    LogLevel.WARNING,
                    "file-read-error",
                    f"Failed to read markdown file: {e}",
                    md_file,
                )

        return all_references

    def validate_unreferenced_files(
        self,
        project_dir: Path,
        relative_to: Path,
        resource_dirs: list[Path],
        markdown_content: str,
        markdown_file: Path,
        content_start_line_number: int = 0,
        ignore_dirs: list[Path] | None = None,
        level: LogLevel = LogLevel.ERROR,
    ) -> tuple[int, int]:
        """
        Validate that all files in resource directories are referenced in the provided markdown content
        and any markdown files referenced by it.

        Args:
            project_dir: Directory to search for resource files
            relative_to: Base directory for relative path resolution
            resource_dirs: List of resource directories to check (e.g., ['assets', 'references', 'scripts'])
            markdown_content: Content of the main markdown file (SKILL.md or AGENTS.md) without the front matter
            markdown_file: Path to the main markdown file
            content_start_line_number: Line number where the markdown content starts (used for accurate logging)
            ignore_dirs: List of directories to ignore
            level: Log level for unreferenced files (ERROR or WARNING)

        Returns:
            Tuple of (warning_count, error_count)
        """

        if ignore_dirs is None:
            ignore_dirs = []

        ignore_paths = [project_dir / ignore_dir for ignore_dir in ignore_dirs]

        warnings = 0
        errors = 0

        # Extract references from the provided markdown content
        all_referenced_files: set[str] = set()
        refs = self.extract_file_references(markdown_content)

        # Process references from the main markdown file
        for ref in refs:
            self._add_resolved_reference(
                ref, markdown_file, project_dir, all_referenced_files, content_start_line_number
            )

        # Also check any markdown files referenced in the main markdown file
        for ref in refs:
            if ref.endswith(".md"):
                try:
                    # Resolve the referenced markdown file
                    if ref.startswith("/"):
                        referenced_md = project_dir / ref.lstrip("/")
                    else:
                        referenced_md = (markdown_file.parent / ref).resolve()

                    if referenced_md.exists() and referenced_md.is_file():
                        # Read and extract references from the referenced markdown file
                        try:
                            referenced_content = referenced_md.read_text()
                            nested_refs = self.extract_file_references(referenced_content)
                            for nested_ref in nested_refs:
                                self._add_resolved_reference(
                                    nested_ref,
                                    referenced_md,
                                    project_dir,
                                    all_referenced_files,
                                    content_start_line_number,
                                )
                        except Exception as e:
                            self.logger.logRule(
                                LogLevel.WARNING,
                                "file-read-error",
                                f"Failed to read referenced markdown file: {e}",
                                referenced_md,
                            )
                except (OSError, RuntimeError) as exc:  # nosec B110, B112 - Skip any unresolvable references
                    self.logger.logRule(
                        LogLevel.WARNING,
                        "reference-resolution-failed",
                        f"Could not resolve markdown reference '{ref}': {exc}",
                        markdown_file,
                        content_start_line_number,
                    )

        self.logger.log(
            LogLevel.DEBUG,
            f"Found the following references: {all_referenced_files}",
        )

        # Check each resource directory
        for resource_dir in resource_dirs:
            resource_path = project_dir / resource_dir
            if not resource_path.exists() or not resource_path.is_dir():
                self.logger.log(
                    LogLevel.DEBUG,
                    f"Resource directory not found: {resource_dir}",
                )
                continue

            # Find all files in resource directory
            for file_path in resource_path.rglob("*"):
                self.logger.log(
                    LogLevel.DEBUG,
                    f"Checking file: {file_path} against above references",
                )
                if file_path.is_file():
                    # Skip ignored directories
                    if any(part == ignored.name for part in file_path.parts for ignored in ignore_paths):
                        continue

                    self.logger.log(
                        LogLevel.DEBUG,
                        f"Checking non ignored file: {file_path} against above references",
                    )
                    try:
                        # Create both relative paths for comparison
                        relative_path_from_relative_to = file_path.relative_to(relative_to)
                        relative_path_from_project = file_path.relative_to(project_dir)

                        project_relative_str = str(relative_path_from_project)

                        # Check if this file is referenced
                        is_referenced = False
                        for ref in all_referenced_files:
                            # Check exact match or if ref ends with this path (comparing with project-relative path)
                            if ref == project_relative_str or ref.endswith(project_relative_str):
                                is_referenced = True
                                break

                        if not is_referenced:
                            project_dir_relative = project_dir.relative_to(relative_to)
                            self.logger.logRule(
                                level,
                                "unreferenced-resource-file",
                                f"File '{relative_path_from_project}' in resource directory "
                                f"is not referenced in any markdown file of the directory {project_dir_relative}.",
                                file=relative_path_from_relative_to,
                                line_number=content_start_line_number,
                            )
                            if level == LogLevel.ERROR:
                                errors += 1
                            elif level == LogLevel.WARNING:
                                warnings += 1

                    except ValueError:
                        # Could not create relative path
                        pass

        return warnings, errors

    def _add_resolved_reference(
        self,
        ref: str,
        markdown_file: Path,
        project_dir: Path,
        all_referenced_files: set[str],
        content_start_line_number: int,
    ) -> None:
        """
        Resolve a file reference and add it to the set of all referenced files.

        Args:
            ref: The file reference to resolve
            markdown_file: The markdown file containing the reference
            project_dir: The project directory
            all_referenced_files: Set to add the resolved reference to
            content_start_line_number: Line number where the markdown content starts (used for accurate logging)
        """
        try:
            if ref.startswith("/"):
                # Absolute path from project root
                resolved = project_dir / ref.lstrip("/")
            else:
                # Relative to markdown file
                resolved = (markdown_file.parent / ref).resolve()

            # Normalize to relative path from project root
            try:
                relative = resolved.relative_to(project_dir)
                all_referenced_files.add(str(relative))
            except ValueError:
                # File is outside project directory, skip
                pass
        except (OSError, RuntimeError) as exc:  # nosec B110, B112 - Skip any unresolvable references
            # Could not resolve path, log and skip it
            self.logger.logRule(
                LogLevel.WARNING,
                "reference-resolution-failed",
                f"Could not resolve reference '{ref}' in markdown file '{markdown_file}': {exc}",
                markdown_file,
                line_number=content_start_line_number,
            )
