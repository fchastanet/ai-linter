import argparse
import os

from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class Arguments:
    """
    Arguments that allows to override config file settings from the command line
    """

    def __init__(
        self,
        skills: bool,
        directories: list[str],
        config_file: str | None,
        log_level: LogLevel | None,
        log_format: LogFormat | None,
        max_warnings: int | None,
    ) -> None:
        self.skills = skills
        self.directories = directories
        self.config_file = config_file
        self.log_level = log_level
        self.log_format = log_format
        self.max_warnings = max_warnings

    @staticmethod
    def parse_arguments(logger: Logger, ai_linter_version: str) -> tuple["Arguments", int]:
        """Parse command line arguments and return Arguments object.

        Returns:
            tuple: (Arguments object, return_code) where return_code is 0 on success, 1 on validation error
        """
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
            version=f"%(prog)s {ai_linter_version}",
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
                return Arguments(False, [], None, None, None, None), 1

        if args.config_file:
            if not os.path.isfile(args.config_file):
                logger.log(
                    LogLevel.ERROR,
                    f"Config file '{args.config_file}' does not exist or is not a file",
                )
                return Arguments(False, [], None, None, None, None), 1

        arguments = Arguments(
            skills=args.skills,
            directories=args.directories,
            log_level=log_level,
            log_format=log_format,
            max_warnings=max_warnings,
            config_file=args.config_file,
        )

        return arguments, 0
