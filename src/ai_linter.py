#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys

from lib.ai.stats import AiStats
from lib.arguments import Arguments
from lib.config import load_config
from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from processors.process_agents import ProcessAgents
from processors.process_projects import ProcessProjects
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
process_projects = ProcessProjects(logger, parser, process_agents, process_prompts)


def validate(
    arguments: Arguments,
) -> tuple[int, int]:
    """Validate skills and agents in the specified directories"""
    # Collect skill directories from project directories
    skill_directories, project_dirs = process_skills.collect_skill_directories(arguments.directories, arguments)

    total_warnings = 0
    total_errors = 0

    # Process skills
    if arguments.skills:
        nb_warnings, nb_errors = process_skills.process_skills_for_directories(skill_directories, arguments)
        total_warnings += nb_warnings
        total_errors += nb_errors

    # Process projects
    nb_warnings, nb_errors = process_projects.process_projects_for_directories(project_dirs, arguments)
    total_warnings += nb_warnings
    total_errors += nb_errors

    # Flush buffered log messages
    logger.flush()

    return total_warnings, total_errors


def main() -> int:
    """Main entry point for the AI Linter"""
    arguments, return_code = Arguments.parse_arguments(logger, AI_LINTER_VERSION)
    if return_code != 0:
        return return_code

    nb_warnings, nb_errors = validate(arguments)
    config = load_config(logger, arguments, arguments.directories[0])

    return 0 if nb_errors == 0 and (arguments.max_warnings == -1 or nb_warnings <= config.max_warnings) else 1


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
