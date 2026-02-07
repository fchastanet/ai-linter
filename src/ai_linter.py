#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import argparse
import os
import sys
from pathlib import Path

from lib.ai.stats import AiStats
from lib.config import load_config
from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from processors.process_agents import ProcessAgents
from processors.process_skills import ProcessSkills
from validators.agent_validator import AgentValidator
from validators.code_snippet_validator import CodeSnippetValidator
from validators.file_reference_validator import FileReferenceValidator
from validators.front_matter_validator import FrontMatterValidator
from validators.skill_validator import SkillValidator
from validators.unreferenced_file_validator import UnreferencedFileValidator

try:
    from _version import version as AI_LINTER_VERSION
except ImportError:
    AI_LINTER_VERSION = "dev"

AI_LINTER_CONFIG_FILE = ".ai-linter-config.yaml"

logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)
parser = Parser(logger)
ai_stats = AiStats(logger)
file_reference_validator = FileReferenceValidator(logger, ai_stats)
front_matter_validator = FrontMatterValidator(logger, parser)


def main() -> None:
    """Main entry point for the AI Linter"""
    arg_parser = argparse.ArgumentParser(description="Quick validation script for skills")
    arg_parser.add_argument(
        "--skills",
        action="store_true",
        help="Indicates that the input directories contain skills",
    )
    arg_parser.add_argument(
        "--max-warnings",
        type=int,
        default=-1,
        help="Maximum number of warnings allowed before failing, -1 for unlimited",
    )
    arg_parser.add_argument(
        "--ignore-dirs",
        type=str,
        nargs="+",
        default=None,
        help="List of directory patterns to ignore when validating AGENTS.md files",
    )
    arg_parser.add_argument(
        "--log-level",
        type=str,
        choices=[level.name for level in LogLevel],
        default=None,
        help="Set the logging level",
    )
    arg_parser.add_argument(
        "--log-format",
        type=str,
        choices=[fmt.value for fmt in LogFormat],
        default=None,
        help="Set the logging format (default: file-digest)",
    )
    arg_parser.add_argument("directories", nargs="+", help="Directories to validate")
    arg_parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {AI_LINTER_VERSION}",
        help="Show the version of the AI Linter",
    )
    arg_parser.add_argument(
        "--config-file",
        type=str,
        default=AI_LINTER_CONFIG_FILE,
        help="Path to the AI Linter configuration file",
    )
    args = arg_parser.parse_args()

    # log level
    log_level = LogLevel.from_string(args.log_level) if args.log_level else LogLevel.INFO

    # log format
    log_format = LogFormat.from_string(args.log_format) if args.log_format else LogFormat.FILE_DIGEST

    # ignore directories
    ignore_dirs = [".git", "__pycache__"]

    # max warnings
    max_warnings = int(args.max_warnings) if args.max_warnings is not None else -1

    # unique directories
    args.directories = list(set(args.directories))

    # config file
    config_file = args.config_file if args.config_file else AI_LINTER_CONFIG_FILE

    # Load configuration file if it exists
    config_path = os.path.join(Path.cwd(), config_file)
    ignore_dirs, log_level, log_format, max_warnings, config = load_config(
        args, logger, config_path, log_level, log_format, ignore_dirs, max_warnings
    )

    # Update logger with config values (config file overridden by CLI args)
    logger.set_level(log_level)
    logger.set_format(log_format)
    code_snippet_validator_intance = CodeSnippetValidator(logger, config.code_snippet_max_lines)
    unreferenced_file_validator = UnreferencedFileValidator(logger)
    skill_validator = SkillValidator(
        logger,
        parser,
        file_reference_validator,
        front_matter_validator,
        unreferenced_file_validator,
        code_snippet_validator_intance,
        config,
    )
    agent_validator = AgentValidator(logger, parser, file_reference_validator, code_snippet_validator_intance)
    process_skills = ProcessSkills(logger, parser, skill_validator)
    process_agents = ProcessAgents(logger, parser, agent_validator)

    # start processing
    start_time = os.times()

    # collect skill directories
    skill_directories = {}
    project_dirs = set()
    skills_count = 0
    for directory in args.directories:
        directory = os.path.abspath(directory)
        if not os.path.isdir(directory):
            logger.log(
                LogLevel.ERROR,
                f"Directory '{directory}' does not exist or is not a directory",
            )
            sys.exit(1)

        if args.skills:
            # look for skills in .github/skills subdirectory
            skills_dir = os.path.abspath(f"{directory}/.github/skills")
            if os.path.exists(skills_dir) and os.path.isdir(skills_dir):
                dirs = [
                    name
                    for name in os.listdir(skills_dir)
                    if os.path.isdir(os.path.join(skills_dir, name))
                    and os.path.exists(os.path.join(skills_dir, name, "SKILL.md"))
                ]
                for skill_dir in dirs:
                    full_skill_dir = os.path.join(skills_dir, skill_dir)
                    if full_skill_dir not in skill_directories:
                        skill_directories[full_skill_dir] = directory
            new_skills_count = len(skill_directories.keys())
            logger.log(
                LogLevel.INFO,
                f"Found {new_skills_count - skills_count} skills in directory '{directory}'",
            )
            skills_count = new_skills_count
            for skill_dir in skill_directories.keys():
                if os.path.isdir(skill_dir):
                    project_dirs.add(str(skill_validator.deduce_project_root_dir_from_skill_dir(skill_dir)))
        else:
            # add the directory if not already present
            if directory not in skill_directories:
                project_dirs.add(directory)

    logger.log(
        LogLevel.INFO,
        f"Found {len(project_dirs)} unique project directories to process: {project_dirs} ",
    )

    total_warnings = 0
    total_errors = 0

    # process skills
    if args.skills:
        for skill_dir, project_dir in skill_directories.items():
            logger.log(
                LogLevel.INFO,
                f"Processing skill directory: {skill_dir} (project: {project_dir})",
            )

            nb_warnings, nb_errors = process_skills.process_skill(Path(skill_dir), Path(project_dir))
            total_warnings += nb_warnings
            total_errors += nb_errors

    nb_warnings, nb_errors = process_agents.process_agents(
        [Path(d) for d in project_dirs], [Path(d) for d in ignore_dirs]
    )
    total_warnings += nb_warnings
    total_errors += nb_errors

    # Flush buffered log messages
    logger.flush()

    logger.log(
        LogLevel.INFO,
        f"Total warnings: {total_warnings}, Total errors: {total_errors}",
    )

    # finish processing
    end_time = os.times()
    elapsed_time = end_time.elapsed - start_time.elapsed
    logger.log(
        LogLevel.INFO,
        f"Linting completed in {elapsed_time:.2f} seconds",
    )

    sys.exit(0 if total_errors == 0 and (max_warnings == -1 or total_warnings <= max_warnings) else 1)


if __name__ == "__main__":
    main()
