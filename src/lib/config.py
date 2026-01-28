import os
from argparse import Namespace

import yaml

from lib.log import Logger, LogLevel


def load_config(
    args: Namespace, logger: Logger, config_path: str, log_level: LogLevel, ignore_dirs: list[str], max_warnings: float
) -> tuple[list[str], LogLevel, float]:
    """Load configuration from a YAML file"""
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
                        logger.log(
                            LogLevel.INFO,
                            "config-max-warnings-set",
                            f"Max warnings set to {max_warnings} from config file",
                        )
                    # Add ignore directories from config
                    if args.ignore_dirs is None and "ignore_dirs" in config and isinstance(config["ignore_dirs"], list):
                        ignore_dirs = config["ignore_dirs"]
                        logger.log(
                            LogLevel.INFO,
                            "config-ignore-dirs-set",
                            f"Ignore directories set to {ignore_dirs} from config file",
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

    return ignore_dirs, log_level, max_warnings
