import re
from pathlib import Path

from lib.log.logger import Logger, LogLevel


class UnreferencedFileValidator:
    """Validator to check that all files in resource directories are referenced in .md files"""

    def __init__(self, logger: Logger):
        self.logger = logger

    def find_all_markdown_files(self, directory: str | Path, ignore_dirs: list[Path] | None = None) -> list[Path]:
        """Find all markdown files in a directory"""
        directory = Path(directory)
        if ignore_dirs is None:
            ignore_dirs = []

        markdown_files = []
        for md_file in directory.rglob("*.md"):
            # Skip ignored directories
            if any(ignored in md_file.parts for ignored in ignore_dirs):
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
        ignore_dirs: list[Path] | None = None,
        level: LogLevel = LogLevel.ERROR,
    ) -> tuple[int, int]:
        """
        Validate that all files in resource directories are referenced in markdown files
        Returns tuple of (warning_count, error_count)
        """

        project_dir = Path(project_dir)
        if ignore_dirs is None:
            ignore_dirs = []

        warnings = 0
        errors = 0

        # Get all references from markdown files
        all_refs = self.get_all_references_in_directory(project_dir, ignore_dirs)
        all_referenced_files = set()

        # Normalize all references
        for md_file, refs in all_refs.items():
            md_path = Path(md_file)
            for ref in refs:
                # Try to resolve relative to markdown file location
                try:
                    if ref.startswith("/"):
                        # Absolute path from project root
                        resolved = project_dir / ref.lstrip("/")
                    else:
                        # Relative to markdown file
                        resolved = (md_path.parent / ref).resolve()

                    # Normalize to relative path from project root
                    try:
                        relative = resolved.relative_to(project_dir)
                        all_referenced_files.add(str(relative))
                    except ValueError:
                        # File is outside project directory, skip
                        pass
                except Exception:  # nosec B110, B112 - Skip any unresolvable references
                    # Could not resolve path, skip it
                    pass

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
                    f"Checking file: {file_path} against references: {all_referenced_files}",
                )
                if file_path.is_file():
                    # Skip ignored directories
                    if any(str(ignored) in file_path.parts for ignored in ignore_dirs):
                        continue

                    self.logger.log(
                        LogLevel.DEBUG,
                        f"Checking non ignored file: {file_path} against references: {all_referenced_files}",
                    )
                    try:
                        relative_path = file_path.relative_to(relative_to)
                        relative_path_str = str(relative_path)

                        # Check if this file is referenced
                        is_referenced = False
                        for ref in all_referenced_files:
                            # Check exact match or if ref ends with this path
                            if ref == relative_path_str or ref.endswith(relative_path_str):
                                is_referenced = True
                                break

                        if not is_referenced:
                            file_path_relative_to_project = file_path.relative_to(project_dir)
                            project_dir_relative = project_dir.relative_to(relative_to)
                            self.logger.logRule(
                                level,
                                "unreferenced-resource-file",
                                f"File '{file_path_relative_to_project}' in resource directory is not referenced"
                                f" in any markdown file of the directory {project_dir_relative}.",
                                file=relative_path,
                            )
                            if level == LogLevel.ERROR:
                                errors += 1
                            elif level == LogLevel.WARNING:
                                warnings += 1

                    except ValueError:
                        # Could not create relative path
                        pass

        return warnings, errors
