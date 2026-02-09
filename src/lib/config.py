import os
from argparse import Namespace

import yaml

from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class Config:
    """Configuration holder for AI Linter"""

    def __init__(self) -> None:
        self.log_level: LogLevel = LogLevel.INFO
        self.log_format: LogFormat = LogFormat.FILE_DIGEST
        self.max_warnings: int = -1
        self.ignore_dirs: list[str] = [".git", "__pycache__"]
        self.code_snippet_max_lines: int = 3
        self.prompt_dirs: list[str] = [".github/prompts"]
        self.agent_dirs: list[str] = [".github/agents"]
        self.resource_dirs: list[str] = ["references", "assets", "scripts"]
        self.unreferenced_file_level: LogLevel = LogLevel.ERROR  # Can be ERROR, WARNING, or INFO
        self.missing_agents_file_level: LogLevel = LogLevel.WARNING  # Level for missing AGENTS.md
        # Report configuration
        self.report_warning_threshold: float = 0.8  # 80% of limit triggers warning
        self.prompt_max_tokens: int = 5000
        self.prompt_max_lines: int = 500
        self.agent_max_tokens: int = 5000
        self.agent_max_lines: int = 500
        # Agent section validation configuration
        self.enable_advices: bool = True  # Enable advice-level recommendations
        self.missing_section_level: LogLevel = LogLevel.WARNING  # Level for missing mandatory sections
        self.mandatory_sections: list[str] = [
            "navigating the codebase",
            "build & commands",
            "using subagents",
            "code style",
            "testing",
            "security",
            "configuration",
        ]
        self.recommended_sections: list[str] = [
            "git commit conventions",
            "architecture",
            "build process",
        ]


def load_config(
    args: Namespace,
    logger: Logger,
    config_path: str,
    log_level: LogLevel,
    log_format: LogFormat,
    ignore_dirs: list[str],
    max_warnings: int,
) -> tuple[list[str], LogLevel, LogFormat, int, Config]:
    """Load configuration from a YAML file"""
    config_obj = Config()
    config_obj.log_level = log_level
    config_obj.log_format = log_format
    config_obj.ignore_dirs = ignore_dirs
    config_obj.max_warnings = max_warnings

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                if isinstance(config, dict):
                    # Override log level if specified in config
                    if (
                        args.log_level is None
                        and "log_level" in config
                        and config["log_level"] in [level.name for level in LogLevel]
                    ):
                        config_obj.log_level = get_log_level_from_string(config["log_level"], LogLevel.INFO)
                        logger.log(
                            LogLevel.INFO,
                            f"Log level set to {config_obj.log_level} from config file",
                        )
                    logger.set_level(config_obj.log_level)

                    # Override log format if specified in config (CLI overrides config)
                    if args.log_format is None and "log_format" in config and isinstance(config["log_format"], str):
                        log_format = LogFormat.from_string(config["log_format"])
                        config_obj.log_format = log_format
                        logger.set_format(log_format)
                        logger.log(
                            LogLevel.INFO,
                            f"Log format set to {log_format.value} from config file",
                        )

                    # Override max warnings if specified in config
                    if (
                        args.max_warnings is None
                        and "max_warnings" in config
                        and isinstance(config["max_warnings"], int)
                    ):
                        max_warnings = config["max_warnings"]
                        config_obj.max_warnings = max_warnings
                        logger.log(
                            LogLevel.INFO,
                            f"Max warnings set to {max_warnings} from config file",
                        )
                    # Add ignore directories from config
                    if args.ignore_dirs is None and "ignore_dirs" in config and isinstance(config["ignore_dirs"], list):
                        ignore_dirs = config["ignore_dirs"]
                        config_obj.ignore_dirs = ignore_dirs
                        logger.log(
                            LogLevel.INFO,
                            f"Ignore directories set to {ignore_dirs} from config file",
                        )

                    # New configuration options
                    if "code_snippet_max_lines" in config and isinstance(config["code_snippet_max_lines"], int):
                        config_obj.code_snippet_max_lines = config["code_snippet_max_lines"]
                        logger.log(
                            LogLevel.INFO,
                            f"Code snippet max lines set to {config_obj.code_snippet_max_lines} from config file",
                        )

                    if "prompt_dirs" in config and isinstance(config["prompt_dirs"], list):
                        config_obj.prompt_dirs = config["prompt_dirs"]
                        logger.log(
                            LogLevel.INFO,
                            f"Prompt directories set to {config_obj.prompt_dirs} from config file",
                        )

                    if "agent_dirs" in config and isinstance(config["agent_dirs"], list):
                        config_obj.agent_dirs = config["agent_dirs"]
                        logger.log(
                            LogLevel.INFO,
                            f"Agent directories set to {config_obj.agent_dirs} from config file",
                        )

                    if "resource_dirs" in config and isinstance(config["resource_dirs"], list):
                        config_obj.resource_dirs = config["resource_dirs"]
                        logger.log(
                            LogLevel.INFO,
                            f"Resource directories set to {config_obj.resource_dirs} from config file",
                        )

                    if "unreferenced_file_level" in config and isinstance(config["unreferenced_file_level"], str):
                        config_obj.unreferenced_file_level = get_log_level_from_string(
                            config["unreferenced_file_level"], LogLevel.ERROR
                        )
                        logger.log(
                            LogLevel.INFO,
                            f"Unreferenced file level set to {config_obj.unreferenced_file_level} from config file",
                        )

                    if "missing_agents_file_level" in config and isinstance(config["missing_agents_file_level"], str):
                        config_obj.missing_agents_file_level = get_log_level_from_string(
                            config["missing_agents_file_level"], LogLevel.WARNING
                        )
                        logger.log(
                            LogLevel.INFO,
                            "Missing AGENTS.md file level set to "
                            f"{config_obj.missing_agents_file_level} from config file",
                        )

                    # Report configuration options
                    if "report_warning_threshold" in config and isinstance(
                        config["report_warning_threshold"], (int, float)
                    ):
                        config_obj.report_warning_threshold = float(config["report_warning_threshold"])
                        logger.log(
                            LogLevel.INFO,
                            f"Report warning threshold set to {config_obj.report_warning_threshold} from config file",
                        )

                    if "prompt_max_tokens" in config and isinstance(config["prompt_max_tokens"], int):
                        config_obj.prompt_max_tokens = config["prompt_max_tokens"]
                        logger.log(
                            LogLevel.INFO,
                            f"Prompt max tokens set to {config_obj.prompt_max_tokens} from config file",
                        )

                    if "prompt_max_lines" in config and isinstance(config["prompt_max_lines"], int):
                        config_obj.prompt_max_lines = config["prompt_max_lines"]
                        logger.log(
                            LogLevel.INFO,
                            f"Prompt max lines set to {config_obj.prompt_max_lines} from config file",
                        )

                    if "agent_max_tokens" in config and isinstance(config["agent_max_tokens"], int):
                        config_obj.agent_max_tokens = config["agent_max_tokens"]
                        logger.log(
                            LogLevel.INFO,
                            f"Agent max tokens set to {config_obj.agent_max_tokens} from config file",
                        )

                    if "agent_max_lines" in config and isinstance(config["agent_max_lines"], int):
                        config_obj.agent_max_lines = config["agent_max_lines"]
                        logger.log(
                            LogLevel.INFO,
                            f"Agent max lines set to {config_obj.agent_max_lines} from config file",
                        )

                    # Agent section validation configuration
                    if "enable_advices" in config and isinstance(config["enable_advices"], bool):
                        config_obj.enable_advices = config["enable_advices"]
                        logger.log(
                            LogLevel.INFO,
                            f"Enable advices set to {config_obj.enable_advices} from config file",
                        )

                    if "missing_section_level" in config and isinstance(config["missing_section_level"], str):
                        config_obj.missing_section_level = get_log_level_from_string(
                            config["missing_section_level"], LogLevel.WARNING
                        )
                        logger.log(
                            LogLevel.INFO,
                            f"Missing section level set to {config_obj.missing_section_level} from config file",
                        )

                    if "mandatory_sections" in config and isinstance(config["mandatory_sections"], list):
                        config_obj.mandatory_sections = config["mandatory_sections"]
                        logger.log(
                            LogLevel.INFO,
                            f"Mandatory sections set to {config_obj.mandatory_sections} from config file",
                        )

                    if "recommended_sections" in config and isinstance(config["recommended_sections"], list):
                        config_obj.recommended_sections = config["recommended_sections"]
                        logger.log(
                            LogLevel.INFO,
                            f"Recommended sections set to {config_obj.recommended_sections} from config file",
                        )

                else:
                    logger.log(
                        LogLevel.WARNING,
                        f"Config file '{config_path}' is not a valid YAML dictionary.",
                    )
            logger.log(
                LogLevel.INFO,
                f"Loaded config file: {config_path}",
            )

        except Exception as e:
            logger.log(
                LogLevel.WARNING,
                f"Failed to load config file '{config_path}': {e}",
            )
    else:
        logger.log(
            LogLevel.INFO,
            f"Config file '{config_path}' not found, using default settings.",
        )

    return config_obj.ignore_dirs, config_obj.log_level, config_obj.log_format, config_obj.max_warnings, config_obj


def get_log_level_from_string(levelStr: str, default: LogLevel) -> LogLevel:
    """Convert string to LogLevel, with default fallback"""
    levelStr = levelStr.upper()
    result = LogLevel.from_string(levelStr)
    # from_string returns INFO for invalid values, so check if we got what we asked for
    # or if it fell back to INFO (unless that's what we wanted)
    if result == LogLevel.INFO and levelStr != "INFO" and levelStr != "INFORMATION":
        return default
    return result
