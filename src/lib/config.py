import os

import yaml

from lib.arguments import Arguments
from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger

MANDATORY_SECTIONS_LOG_LEVELS = [LogLevel.ERROR, LogLevel.WARNING]
DEFAULT_IGNORE_PATTERNS = [".git", "__pycache__"]
AI_LINTER_CONFIG_FILE = ".ai-linter-config.yaml"


class Config:
    """Configuration holder for AI Linter"""

    def __init__(self) -> None:
        self.log_level: LogLevel = LogLevel.INFO
        self.log_format: LogFormat = LogFormat.FILE_DIGEST
        self.max_warnings: int = -1
        self.ignore: list[str] = list(DEFAULT_IGNORE_PATTERNS)  # Glob patterns for files and directories
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
        self.enable_advised_sections: bool = True  # Enable advice-level recommendations
        self.enable_mandatory_sections: bool = True  # Enable mandatory section validation
        self.mandatory_sections_log_level: LogLevel = LogLevel.WARNING  # Level for missing mandatory sections
        self.mandatory_sections: dict[str, str] = {
            "overview": "Overview",
            "limitations": "Limitations",
            "navigating the codebase": "Navigating the Codebase",
            "build & commands": "Build & Commands",
            "code style": "Code Style",
            "testing": "Testing",
            "security": "Security",
            "configuration": "Configuration",
        }
        self.advised_sections: dict[str, str] = {
            "architecture": "Architecture",
            "build process": "Build Process",
            "git commit conventions": "Git Commit Conventions",
            "troubleshooting": "Troubleshooting",
        }


def load_config(logger: Logger, args: Arguments, project_dir: str) -> Config:
    """
    Load configuration from :
    - config file argument if provided
    - from default config file in project directory
    - from current directory if default config file found there
    - default config if no config file found
    """
    config_file = None
    if args.config_file:
        logger.log(
            LogLevel.DEBUG,
            f"Using config file from argument: '{args.config_file}'",
        )
        config_file = args.config_file
    else:
        # look for config file in project directory
        logger.log(
            LogLevel.DEBUG,
            f"Looking for config file in project directory '{project_dir}'",
        )
        project_config_file = os.path.join(project_dir, AI_LINTER_CONFIG_FILE)
        if os.path.isfile(project_config_file):
            config_file = project_config_file
        else:
            logger.log(
                LogLevel.DEBUG,
                f"No config file found in project directory '{project_dir}', looking in current directory",
            )
            current_dir_config_file = os.path.join(os.getcwd(), AI_LINTER_CONFIG_FILE)
            if os.path.isfile(current_dir_config_file):
                config_file = current_dir_config_file

    return _load_config_file(args, logger, config_file, LogLevel.INFO, LogFormat.FILE_DIGEST, -1)


def _load_config_file(
    args: Arguments,
    logger: Logger,
    config_path: str | None,
    log_level: LogLevel,
    log_format: LogFormat,
    max_warnings: int,
) -> Config:
    """Load configuration from a YAML file"""
    config_obj = Config()
    config_obj.log_level = log_level
    config_obj.log_format = log_format
    config_obj.ignore = list(DEFAULT_IGNORE_PATTERNS)
    config_obj.max_warnings = max_warnings

    if config_path is None:
        return config_obj

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                if isinstance(config, dict):
                    _update_config_from_dict(args, config_obj, config, logger)
                    logger.log(
                        LogLevel.DEBUG,
                        f"Loaded config file: {config_path}",
                    )
                elif config is None:
                    logger.log(
                        LogLevel.DEBUG,
                        f"Config file '{config_path}' is empty; using default settings.",
                    )
                else:
                    logger.log(
                        LogLevel.WARNING,
                        f"Config file '{config_path}' is not a valid YAML dictionary.",
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

    return config_obj


def _update_config_from_dict(args: Arguments, config_obj: Config, config: dict, logger: Logger) -> None:
    """Update Config object from a dictionary, with validation and logging"""
    # Override log level if specified in config
    if hasattr(args, "log_level") and args.log_level is not None:
        logger.log(
            LogLevel.DEBUG,
            f"Log level specified in arguments ({args.log_level}) takes precedence over config file",
        )
        config_obj.log_level = args.log_level
    elif (
        "log_level" in config and isinstance(config["log_level"], str) and LogLevel.is_valid_string(config["log_level"])
    ):
        config_obj.log_level = get_log_level_from_string(config["log_level"], LogLevel.INFO)
        logger.log(
            LogLevel.INFO,
            f"Log level set to {config_obj.log_level} from config file",
        )
    logger.set_level(config_obj.log_level)

    # Override max warnings if specified in config
    if hasattr(args, "max_warnings") and args.max_warnings is not None:
        logger.log(
            LogLevel.DEBUG,
            f"Max warnings specified in arguments ({args.max_warnings}) takes precedence over config file",
        )
        config_obj.max_warnings = args.max_warnings
    elif "max_warnings" in config and isinstance(config["max_warnings"], int):
        max_warnings = config["max_warnings"]
        config_obj.max_warnings = max_warnings
        logger.log(
            LogLevel.INFO,
            f"Max warnings set to {max_warnings} from config file",
        )

    # Override log format if specified in config
    if hasattr(args, "log_format") and args.log_format is not None:
        logger.log(
            LogLevel.DEBUG,
            f"Log format specified in arguments ({args.log_format}) takes precedence over config file",
        )
        config_obj.log_format = args.log_format
    elif (
        "log_format" in config
        and isinstance(config["log_format"], str)
        and LogFormat.is_valid_string(config["log_format"])
    ):
        config_obj.log_format = LogFormat.from_string(config["log_format"])
        logger.log(
            LogLevel.INFO,
            f"Log format set to {config_obj.log_format} from config file",
        )

    # Add ignore patterns from config
    if hasattr(args, "ignore") and args.ignore is not None:
        logger.log(
            LogLevel.DEBUG,
            f"Ignore patterns specified in arguments ({args.ignore}) takes precedence over config file",
        )
        config_obj.ignore = args.ignore
    elif "ignore" in config and isinstance(config["ignore"], list):
        ignore_patterns = config["ignore"]
        config_key = "ignore"
        if ignore_patterns is not None:
            config_obj.ignore = ignore_patterns
            logger.log(
                LogLevel.DEBUG,
                f"Ignore patterns set to {ignore_patterns} from config file (key: {config_key})",
            )

    # New configuration options
    if "code_snippet_max_lines" in config and isinstance(config["code_snippet_max_lines"], int):
        config_obj.code_snippet_max_lines = config["code_snippet_max_lines"]
        logger.log(
            LogLevel.DEBUG,
            f"Code snippet max lines set to {config_obj.code_snippet_max_lines} from config file",
        )

    if "prompt_dirs" in config and isinstance(config["prompt_dirs"], list):
        config_obj.prompt_dirs = config["prompt_dirs"]
        logger.log(
            LogLevel.DEBUG,
            f"Prompt directories set to {config_obj.prompt_dirs} from config file",
        )

    if "agent_dirs" in config and isinstance(config["agent_dirs"], list):
        config_obj.agent_dirs = config["agent_dirs"]
        logger.log(
            LogLevel.DEBUG,
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
            LogLevel.DEBUG,
            f"Unreferenced file level set to {config_obj.unreferenced_file_level} from config file",
        )

    if "missing_agents_file_level" in config and isinstance(config["missing_agents_file_level"], str):
        config_obj.missing_agents_file_level = get_log_level_from_string(
            config["missing_agents_file_level"], LogLevel.WARNING
        )
        logger.log(
            LogLevel.DEBUG,
            "Missing AGENTS.md file level set to " f"{config_obj.missing_agents_file_level} from config file",
        )

    # Report configuration options
    if "report_warning_threshold" in config and isinstance(config["report_warning_threshold"], (int, float)):
        config_obj.report_warning_threshold = float(config["report_warning_threshold"])
        logger.log(
            LogLevel.DEBUG,
            f"Report warning threshold set to {config_obj.report_warning_threshold} from config file",
        )

    if "prompt_max_tokens" in config and isinstance(config["prompt_max_tokens"], int):
        config_obj.prompt_max_tokens = config["prompt_max_tokens"]
        logger.log(
            LogLevel.DEBUG,
            f"Prompt max tokens set to {config_obj.prompt_max_tokens} from config file",
        )

    if "prompt_max_lines" in config and isinstance(config["prompt_max_lines"], int):
        config_obj.prompt_max_lines = config["prompt_max_lines"]
        logger.log(
            LogLevel.DEBUG,
            f"Prompt max lines set to {config_obj.prompt_max_lines} from config file",
        )

    if "agent_max_tokens" in config and isinstance(config["agent_max_tokens"], int):
        config_obj.agent_max_tokens = config["agent_max_tokens"]
        logger.log(
            LogLevel.DEBUG,
            f"Agent max tokens set to {config_obj.agent_max_tokens} from config file",
        )

    if "agent_max_lines" in config and isinstance(config["agent_max_lines"], int):
        config_obj.agent_max_lines = config["agent_max_lines"]
        logger.log(
            LogLevel.DEBUG,
            f"Agent max lines set to {config_obj.agent_max_lines} from config file",
        )

    if "enable_mandatory_sections" in config and isinstance(config["enable_mandatory_sections"], bool):
        config_obj.enable_mandatory_sections = config["enable_mandatory_sections"]
        logger.log(
            LogLevel.DEBUG,
            f"Enable mandatory section validation set to " f"{config_obj.enable_mandatory_sections} from config file",
        )

    if (
        "mandatory_sections_log_level" in config
        and isinstance(config["mandatory_sections_log_level"], str)
        and config["mandatory_sections_log_level"] in [level.name for level in MANDATORY_SECTIONS_LOG_LEVELS]
    ):
        config_obj.mandatory_sections_log_level = get_log_level_from_string(
            config["mandatory_sections_log_level"], LogLevel.WARNING
        )
        logger.log(
            LogLevel.DEBUG,
            f"Mandatory sections log level set to {config_obj.mandatory_sections_log_level} from config file",
        )

    if "mandatory_sections" in config and isinstance(config["mandatory_sections"], list):
        config_obj.mandatory_sections = _convert_str_list_to_dict(config["mandatory_sections"])
        logger.log(
            LogLevel.DEBUG,
            f"Mandatory sections set to {config_obj.mandatory_sections} from config file",
        )

    # Agent section validation configuration
    if "enable_advised_sections" in config and isinstance(config["enable_advised_sections"], bool):
        config_obj.enable_advised_sections = config["enable_advised_sections"]
        logger.log(
            LogLevel.DEBUG,
            f"Enable advised section set to {config_obj.enable_advised_sections} from config file",
        )

    if "advised_sections" in config and isinstance(config["advised_sections"], list):
        config_obj.advised_sections = _convert_str_list_to_dict(config["advised_sections"])
        logger.log(
            LogLevel.DEBUG,
            f"Advised sections set to {config_obj.advised_sections} from config file",
        )


def _convert_str_list_to_dict(value: list) -> dict[str, str]:
    """Convert list items to lowercase stripped keys with original string values for easy lookup"""
    converted_dict = dict()
    for item in value:
        item_str = item if isinstance(item, str) else str(item)
        converted_dict[item_str.lower().strip()] = item_str
    return converted_dict


def get_log_level_from_string(level_str: str, default: LogLevel) -> LogLevel:
    """Convert string to LogLevel, with default fallback"""
    if LogLevel.is_valid_string(level_str):
        return LogLevel.from_string(level_str)
    return default
