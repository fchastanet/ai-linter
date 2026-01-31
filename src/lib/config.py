import os
from argparse import Namespace

import yaml

from lib.log import Logger, LogLevel


class Config:
    """Configuration holder for AI Linter"""

    def __init__(self) -> None:
        self.log_level: LogLevel = LogLevel.INFO
        self.max_warnings: float = float("inf")
        self.ignore_dirs: list[str] = [".git", "__pycache__"]
        self.code_snippet_max_lines: int = 3
        self.prompt_dirs: list[str] = [".github/prompts"]
        self.agent_dirs: list[str] = [".github/agents"]
        self.resource_dirs: list[str] = ["references", "assets", "scripts"]
        self.unreferenced_file_level: str = "ERROR"  # Can be ERROR, WARNING, or INFO
        self.missing_agents_file_level: str = "WARNING"  # Level for missing AGENTS.md


def load_config(
    args: Namespace, logger: Logger, config_path: str, log_level: LogLevel, ignore_dirs: list[str], max_warnings: float
) -> tuple[list[str], LogLevel, float, Config]:
    """Load configuration from a YAML file"""
    config_obj = Config()
    config_obj.log_level = log_level
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
                        log_level = LogLevel.from_string(config["log_level"])
                        config_obj.log_level = log_level
                    logger.set_level(log_level)
                    logger.log(
                        LogLevel.INFO,
                        "config-log-level-set",
                        f"Log level set to {log_level} from config file",
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
                            "config-max-warnings-set",
                            f"Max warnings set to {max_warnings} from config file",
                        )
                    # Add ignore directories from config
                    if args.ignore_dirs is None and "ignore_dirs" in config and isinstance(config["ignore_dirs"], list):
                        ignore_dirs = config["ignore_dirs"]
                        config_obj.ignore_dirs = ignore_dirs
                        logger.log(
                            LogLevel.INFO,
                            "config-ignore-dirs-set",
                            f"Ignore directories set to {ignore_dirs} from config file",
                        )

                    # New configuration options
                    if "code_snippet_max_lines" in config and isinstance(config["code_snippet_max_lines"], int):
                        config_obj.code_snippet_max_lines = config["code_snippet_max_lines"]
                        logger.log(
                            LogLevel.INFO,
                            "config-code-snippet-max-lines-set",
                            f"Code snippet max lines set to {config_obj.code_snippet_max_lines} from config file",
                        )

                    if "prompt_dirs" in config and isinstance(config["prompt_dirs"], list):
                        config_obj.prompt_dirs = config["prompt_dirs"]
                        logger.log(
                            LogLevel.INFO,
                            "config-prompt-dirs-set",
                            f"Prompt directories set to {config_obj.prompt_dirs} from config file",
                        )

                    if "agent_dirs" in config and isinstance(config["agent_dirs"], list):
                        config_obj.agent_dirs = config["agent_dirs"]
                        logger.log(
                            LogLevel.INFO,
                            "config-agent-dirs-set",
                            f"Agent directories set to {config_obj.agent_dirs} from config file",
                        )

                    if "resource_dirs" in config and isinstance(config["resource_dirs"], list):
                        config_obj.resource_dirs = config["resource_dirs"]
                        logger.log(
                            LogLevel.INFO,
                            "config-resource-dirs-set",
                            f"Resource directories set to {config_obj.resource_dirs} from config file",
                        )

                    if "unreferenced_file_level" in config and isinstance(config["unreferenced_file_level"], str):
                        config_obj.unreferenced_file_level = config["unreferenced_file_level"].upper()
                        logger.log(
                            LogLevel.INFO,
                            "config-unreferenced-file-level-set",
                            f"Unreferenced file level set to {config_obj.unreferenced_file_level} from config file",
                        )

                    if "missing_agents_file_level" in config and isinstance(config["missing_agents_file_level"], str):
                        config_obj.missing_agents_file_level = config["missing_agents_file_level"].upper()
                        logger.log(
                            LogLevel.INFO,
                            "config-missing-agents-file-level-set",
                            f"Missing AGENTS.md file level set to "
                            f"{config_obj.missing_agents_file_level} from config file",
                        )

                else:
                    logger.log(
                        LogLevel.WARNING,
                        "invalid-config-format",
                        f"Config file '{config_path}' is not a valid YAML dictionary.",
                    )
            logger.log(
                LogLevel.INFO,
                "loaded-config",
                f"Loaded config file: {config_path}",
            )

        except Exception as e:
            logger.log(
                LogLevel.WARNING,
                "config-load-error",
                f"Failed to load config file '{config_path}': {e}",
            )
    else:
        logger.log(
            LogLevel.INFO,
            "config-not-found",
            f"Config file '{config_path}' not found, using default settings.",
        )

    return ignore_dirs, log_level, max_warnings, config_obj
