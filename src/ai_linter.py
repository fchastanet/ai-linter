#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import argparse
import fnmatch
import os
import sys
from pathlib import Path

from lib.ai.stats import AiStats
from lib.config import Arguments, load_config
from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from processors.process_agents import ProcessAgents
from processors.process_prompts import ProcessPrompts
from processors.process_skills import ProcessSkills
from validators.agent_validator import AgentValidator
from validators.code_snippet_validator import CodeSnippetValidator
from validators.content_length_validator import ContentLengthValidator
from validators.file_reference_validator import FileReferenceValidator
from validators.front_matter_validator import FrontMatterValidator
from validators.skill_validator import SkillValidator

try:
    from _version import version as AI_LINTER_VERSION
except ImportError:
    AI_LINTER_VERSION = "dev"


logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)
parser = Parser(logger)
ai_stats = AiStats(logger)
content_length_validator = ContentLengthValidator(logger, ai_stats)
file_reference_validator = FileReferenceValidator(logger, parser)
front_matter_validator = FrontMatterValidator(logger, parser)
code_snippet_validator_instance = CodeSnippetValidator(logger)
skill_validator = SkillValidator(
    logger,
    parser,
    content_length_validator,
    file_reference_validator,
    front_matter_validator,
    code_snippet_validator_instance,
)
agent_validator = AgentValidator(
    logger,
    parser,
    content_length_validator,
    file_reference_validator,
    code_snippet_validator_instance,
)
process_skills = ProcessSkills(logger, parser, skill_validator)
process_agents = ProcessAgents(logger, parser, agent_validator)
process_prompts = ProcessPrompts(logger, parser, content_length_validator, file_reference_validator)


def validate(
    arguments: Arguments,
) -> tuple[int, int]:
    """Validate skills and agents in the specified directories"""
    skills = arguments.skills
    directories = arguments.directories

    # collect skill directories
    skill_directories = {}
    project_dirs = set()
    skills_count = 0
    for directory in directories:
        directory = os.path.abspath(directory)
        project_dirs.add(directory)
        if skills:
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
    if skills:
        for skill_dir, project_dir in skill_directories.items():
            config = load_config(logger, arguments, project_dir)
            # check if skill_dir should be ignored based on ignore patterns
            if any(fnmatch.fnmatch(str(skill_dir), str(pattern)) for pattern in config.ignore):
                logger.log(
                    LogLevel.INFO,
                    f"Skipping skill directory '{skill_dir}' as it matches ignore patterns",
                )
                continue
            logger.log(
                LogLevel.INFO,
                f"Processing skill directory: {skill_dir} (project: {project_dir})",
            )

            nb_warnings, nb_errors = process_skills.process_skill(Path(skill_dir), Path(project_dir), config)
            total_warnings += nb_warnings
            total_errors += nb_errors

    for project_dir in project_dirs:
        config = load_config(logger, arguments, project_dir)
        # check if project dir matches any ignore glob pattern
        if any(fnmatch.fnmatch(str(project_dir), str(pattern)) for pattern in config.ignore):
            logger.log(
                LogLevel.DEBUG,
                f"Ignoring project directory '{project_dir}' due to ignore setting: {config.ignore}",
            )
            continue
        project_path = Path(project_dir)
        # Process agents in AGENTS.md files
        nb_warnings, nb_errors = process_agents.process_agents(project_path, config)
        total_warnings += nb_warnings
        total_errors += nb_errors

        # Process prompts in .github/prompts directories
        nb_warnings, nb_errors = process_prompts.process_sub_directories(
            project_path,
            config.ignore,
            "Prompt",
            config.prompt_dirs,
            config.prompt_max_tokens,
            config.prompt_max_lines,
            config.report_warning_threshold,
        )
        total_warnings += nb_warnings
        total_errors += nb_errors

        # Process agents in .github/agents directories (excluding AGENTS.md)
        nb_warnings, nb_errors = process_prompts.process_sub_directories(
            project_path,
            config.ignore,
            "Agent",
            config.agent_dirs,
            config.agent_max_tokens,
            config.agent_max_lines,
            config.report_warning_threshold,
        )
        total_warnings += nb_warnings
        total_errors += nb_errors

    # Flush buffered log messages
    logger.flush()

    return total_warnings, total_errors


def main() -> int:
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
        help="Glob patterns for files and directories to ignore (supports wildcards: *, ?, [seq], [!seq])",
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
        help="Path to the AI Linter configuration file",
    )
    args = arg_parser.parse_args()

    # log level
    log_level = LogLevel.from_string(args.log_level) if args.log_level else None
    # temporarily set to INFO waiting for config to be loaded, which may override this log level
    logger.set_level(LogLevel.INFO if not log_level else log_level)

    # log format
    log_format = LogFormat.from_string(args.log_format) if args.log_format else None
    logger.set_format(LogFormat.FILE_DIGEST if not log_format else log_format)

    # max warnings
    max_warnings = int(args.max_warnings) if args.max_warnings is not None else None

    # unique directories
    args.directories = list(set(args.directories))

    # check that directories exist
    for directory in args.directories:
        directory = os.path.abspath(directory)
        if not os.path.isdir(directory):
            logger.log(
                LogLevel.ERROR,
                f"Directory '{directory}' does not exist or is not a directory",
            )
            return 1

    if args.config_file:
        if not os.path.isfile(args.config_file):
            logger.log(
                LogLevel.ERROR,
                f"Config file '{args.config_file}' does not exist or is not a file",
            )
            return 1

    arguments = Arguments(
        skills=args.skills,
        directories=args.directories,
        log_level=log_level,
        log_format=log_format,
        max_warnings=max_warnings,
        config_file=args.config_file,
    )

    nb_warnings, nb_errors = validate(arguments)
    config = load_config(logger, arguments, args.directories[0])

    return 0 if nb_errors == 0 and (max_warnings == -1 or nb_warnings <= config.max_warnings) else 1


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
