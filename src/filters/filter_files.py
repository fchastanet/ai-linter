from collections.abc import Sequence
from pathlib import Path

import pathspec

from lib.log.log_level import LogLevel
from lib.log.logger import Logger


def filter_files(
    logger: Logger, ignore_patterns: Sequence[str], files: Sequence[Path], project_dir: Path
) -> Sequence[Path]:
    # Create a pathspec from ignore patterns
    spec = pathspec.PathSpec.from_lines("gitignore", ignore_patterns)

    # Filter files: keep only those that DON'T match any ignore pattern
    # Use .as_posix() to ensure cross-platform compatibility with gitignore-style matching
    filtered_files = [f for f in files if not spec.match_file(f.relative_to(project_dir).as_posix())]

    if len(filtered_files) < len(files):
        ignored_files = set(files) - set(filtered_files)
        logger.log(
            LogLevel.DEBUG,
            "Skipping %d file(s) as they match ignore patterns: %s",
            len(ignored_files),
            [f.relative_to(project_dir).as_posix() for f in ignored_files],
        )
    logger.log(
        LogLevel.INFO,
        "Found %d/%d file(s) to validate after applying ignore patterns",
        len(filtered_files),
        len(files),
    )
    return filtered_files


def is_ignored_path(logger: Logger, ignore_patterns: Sequence[str], file: Path) -> bool:
    spec = pathspec.PathSpec.from_lines("gitignore", ignore_patterns)
    is_ignored = spec.match_file(file.as_posix())
    if is_ignored:
        logger.log(
            LogLevel.DEBUG,
            "Skipping path %s as it matches ignore patterns",
            file.as_posix(),
        )
    return is_ignored
