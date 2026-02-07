import re
from pathlib import Path

from lib.log import Logger, LogLevel


class UnreferencedFileValidator:
    """Validator to check that files in specific directories are referenced in markdown content"""

    # Directories that should be checked for unreferenced files
    CHECKED_DIRECTORIES = ["assets", "references", "scripts"]

    def __init__(self, logger: Logger):
        self.logger = logger

    def validate_unreferenced_files(self, base_dir: Path, main_file: Path, content: str) -> tuple[int, int]:
        """
        Validate that all files in assets/, references/, and scripts/ directories
        are referenced in the provided markdown content.

        Args:
            base_dir: Base directory to search for files (typically skill directory or project root)
            main_file: The main file being validated (SKILL.md or AGENTS.md)
            content: The content of the main file (and potentially referenced markdown files)

        Returns:
            tuple[int, int]: (warning_count, error_count)
        """
        warning_count = 0
        error_count = 0

        # Find all files in the checked directories
        files_to_check = self._find_files_in_directories(base_dir)

        if not files_to_check:
            self.logger.log(
                LogLevel.DEBUG,
                "no-files-to-check",
                f"No files found in {self.CHECKED_DIRECTORIES} directories",
                main_file,
            )
            return warning_count, error_count

        # Extract all file references from content
        referenced_files = self._extract_file_references(content)

        # Check for unreferenced files
        for file_path in files_to_check:
            relative_path = file_path.relative_to(base_dir)
            if not self._is_file_referenced(relative_path, referenced_files):
                self.logger.log(
                    LogLevel.WARNING,
                    "unreferenced-file",
                    f"File '{relative_path}' is not referenced in {main_file.name}",
                    main_file,
                )
                warning_count += 1

        return warning_count, error_count

    def _find_files_in_directories(self, base_dir: Path) -> list[Path]:
        """Find all files in the specified directories under base_dir"""
        files: list[Path] = []

        for dir_name in self.CHECKED_DIRECTORIES:
            dir_path = base_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                # Find all files recursively in this directory
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        files.append(file_path)
                        self.logger.log(
                            LogLevel.DEBUG,
                            "file-found-for-reference-check",
                            f"Found file to check: {file_path.relative_to(base_dir)}",
                        )

        return files

    def _extract_file_references(self, content: str) -> set[str]:
        """
        Extract all file references from markdown content.
        This includes:
        - Inline links: `file/path`
        - Markdown links: [text](file/path)
        - Image references: ![alt](file/path)
        """
        references: set[str] = set()

        # Pattern 1: Inline backtick references like `assets/file.txt`
        # Match backtick content that looks like a file path
        for match in re.finditer(r"(?<!`)`(?P<link>[^`\n]+)`(?!`)", content):
            link = match.group("link")
            # Check if it looks like a file path:
            # - Must contain at least one forward slash
            # - Cannot contain wildcards (* or ?)
            # - Cannot contain special shell/filesystem characters (\ < > $ | : " ')
            # This regex pattern uses a positive lookahead to ensure a slash is present,
            # then matches characters that are valid in file paths
            if re.search(r"^(?=[^*?]*\/)[^*?\\<>$|:\"']+$", link):
                references.add(link)
                references.add(self._normalize_path(link))

        # Pattern 2: Markdown links [text](path) or ![alt](path)
        for match in re.finditer(r"!?\[([^\]]*)\]\(([^)]+)\)", content):
            link = match.group(2)
            # Remove any anchor or query string
            link = re.sub(r"[#?].*$", "", link)
            if link:
                references.add(link)
                references.add(self._normalize_path(link))

        return references

    def _normalize_path(self, path: str) -> str:
        """
        Normalize a file path by:
        - Resolving relative paths (../, ./)
        - Removing leading ./
        """
        # Remove leading ./
        path = re.sub(r"^\.\/", "", path)
        # Simple relative path resolution (handle ../)
        parts = path.split("/")
        normalized: list[str] = []
        for part in parts:
            if part == "..":
                if normalized:
                    normalized.pop()
            elif part != "." and part != "":
                normalized.append(part)
        return "/".join(normalized)

    def _is_file_referenced(self, file_path: Path, references: set[str]) -> bool:
        """
        Check if a file path is referenced in the set of references.
        We check multiple variations:
        - Exact match: assets/file.txt
        - Relative paths: ../assets/file.txt, ../../assets/file.txt
        """
        file_path_str = str(file_path).replace("\\", "/")

        # Check exact match
        if file_path_str in references:
            return True

        # Check with various relative path prefixes
        for ref in references:
            # Normalize the reference
            normalized_ref = self._normalize_path(ref)
            if normalized_ref == file_path_str:
                return True
            # Also check if the reference ends with our file path
            # This handles cases like ../../assets/file.txt referencing assets/file.txt
            if normalized_ref.endswith(file_path_str):
                return True

        return False
