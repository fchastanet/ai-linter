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
    filtered_files = [f for f in files if not spec.match_file(str(f.relative_to(project_dir)))]

    if len(filtered_files) < len(files):
        ignored_files = set(files) - set(filtered_files)
        logger.log(
            LogLevel.DEBUG,
            "Skipping file(s) as they match ignore patterns",
            {
                "ignored_files_count": len(ignored_files),
                "ignored_files": [str(f.relative_to(project_dir)) for f in ignored_files],
            },
        )
    logger.log(
        LogLevel.INFO,
        "Found file(s) to validate after applying ignore patterns",
        {"filtered_files_count": len(filtered_files), "total_files_count": len(files)},
    )
    return filtered_files
