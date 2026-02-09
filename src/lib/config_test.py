from argparse import Namespace
from pathlib import Path

import yaml

from lib.config import Config, get_log_level_from_string, load_config
from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class TestConfig:
    """Test Config class functionality"""

    def test_config_defaults(self) -> None:
        """Test that Config has expected default values"""
        config = Config()

        assert config.log_level == LogLevel.INFO
        assert config.log_format == LogFormat.FILE_DIGEST
        assert config.max_warnings == -1
        assert ".git" in config.ignore_dirs
        assert "__pycache__" in config.ignore_dirs
        assert config.code_snippet_max_lines == 3
        assert config.report_warning_threshold == 0.8
        assert config.unreferenced_file_level == LogLevel.ERROR
        assert config.missing_agents_file_level == LogLevel.WARNING

        # Test new defaults
        assert config.enable_section_mandatory is True
        assert config.enable_section_advices is True
        assert config.missing_section_level == LogLevel.WARNING
        assert len(config.mandatory_sections) == 8
        assert "Navigating the Codebase" in config.mandatory_sections
        assert "Build & Commands" in config.mandatory_sections
        assert "Security" in config.mandatory_sections
        assert len(config.recommended_sections) == 4
        assert "Git Commit Conventions" in config.recommended_sections
        assert "Architecture" in config.recommended_sections

    def test_get_log_level_from_string(self) -> None:
        """Test get_log_level_from_string function"""
        assert get_log_level_from_string("ERROR", LogLevel.INFO) == LogLevel.ERROR
        assert get_log_level_from_string("WARNING", LogLevel.INFO) == LogLevel.WARNING
        assert get_log_level_from_string("ADVICE", LogLevel.INFO) == LogLevel.ADVICE
        assert get_log_level_from_string("INFO", LogLevel.ERROR) == LogLevel.INFO
        assert get_log_level_from_string("DEBUG", LogLevel.ERROR) == LogLevel.DEBUG

        # Test case insensitivity
        assert get_log_level_from_string("error", LogLevel.INFO) == LogLevel.ERROR
        assert get_log_level_from_string("advice", LogLevel.INFO) == LogLevel.ADVICE

        # Test INFO synonyms
        assert get_log_level_from_string("INFORMATION", LogLevel.ERROR) == LogLevel.INFO
        assert get_log_level_from_string("INFOR", LogLevel.ERROR) == LogLevel.INFO

        # Test invalid values return default
        assert get_log_level_from_string("INVALID", LogLevel.WARNING) == LogLevel.WARNING
        assert get_log_level_from_string("UNKNOWN", LogLevel.ERROR) == LogLevel.ERROR

    def test_load_config_no_file(self, tmp_path: Path) -> None:
        """Test load_config when config file doesn't exist"""
        logger = Logger(LogLevel.INFO)
        args = Namespace(log_level=None, log_format=None, max_warnings=None, ignore_dirs=None)
        config_path = str(tmp_path / "nonexistent.yaml")

        ignore_dirs, log_level, log_format, max_warnings, config = load_config(
            args, logger, config_path, LogLevel.INFO, LogFormat.FILE_DIGEST, [], -1
        )

        assert log_level == LogLevel.INFO
        assert log_format == LogFormat.FILE_DIGEST
        assert max_warnings == -1
        assert isinstance(config, Config)

    def test_load_config_empty_file(self, tmp_path: Path) -> None:
        """Test load_config with empty YAML file"""
        logger = Logger(LogLevel.INFO)
        args = Namespace(log_level=None, log_format=None, max_warnings=None, ignore_dirs=None)
        config_path = tmp_path / "empty.yaml"
        config_path.write_text("")

        ignore_dirs, log_level, log_format, max_warnings, config = load_config(
            args, logger, str(config_path), LogLevel.INFO, LogFormat.FILE_DIGEST, [], -1
        )

        assert log_level == LogLevel.INFO
        assert isinstance(config, Config)

    def test_load_config_with_section_settings(self, tmp_path: Path) -> None:
        """Test load_config with section validation settings"""
        logger = Logger(LogLevel.INFO)
        args = Namespace(log_level=None, log_format=None, max_warnings=None, ignore_dirs=None)
        config_path = tmp_path / "config.yaml"

        config_data = {
            "enable_section_mandatory": False,
            "enable_section_advices": False,
            "missing_section_level": "ERROR",
            "mandatory_sections": ["security", "testing"],
            "recommended_sections": ["architecture", "deployment"],
        }
        config_path.write_text(yaml.dump(config_data))

        ignore_dirs, log_level, log_format, max_warnings, config = load_config(
            args, logger, str(config_path), LogLevel.INFO, LogFormat.FILE_DIGEST, [], -1
        )

        assert config.enable_section_advices is False
        assert config.enable_section_mandatory is False
        assert config.missing_section_level == LogLevel.ERROR
        assert config.mandatory_sections == ["security", "testing"]
        assert config.recommended_sections == ["architecture", "deployment"]

    def test_load_config_with_log_level(self, tmp_path: Path) -> None:
        """Test load_config with log level in config file"""
        logger = Logger(LogLevel.INFO)
        args = Namespace(log_level=None, log_format=None, max_warnings=None, ignore_dirs=None)
        config_path = tmp_path / "config.yaml"

        config_data = {"log_level": "WARNING"}
        config_path.write_text(yaml.dump(config_data))

        ignore_dirs, log_level, log_format, max_warnings, config = load_config(
            args, logger, str(config_path), LogLevel.INFO, LogFormat.FILE_DIGEST, [], -1
        )

        assert log_level == LogLevel.WARNING
        assert config.log_level == LogLevel.WARNING

    def test_load_config_cli_overrides_file(self, tmp_path: Path) -> None:
        """Test that CLI arguments override config file"""
        logger = Logger(LogLevel.INFO)
        args = Namespace(log_level="DEBUG", log_format=None, max_warnings=5, ignore_dirs=None)
        config_path = tmp_path / "config.yaml"

        config_data = {
            "log_level": "WARNING",
            "max_warnings": 10,
        }
        config_path.write_text(yaml.dump(config_data))

        ignore_dirs, log_level, log_format, max_warnings, config = load_config(
            args, logger, str(config_path), LogLevel.DEBUG, LogFormat.FILE_DIGEST, [], 5
        )

        # CLI overrides file
        assert log_level == LogLevel.DEBUG
        assert max_warnings == 5

    def test_load_config_with_all_options(self, tmp_path: Path) -> None:
        """Test load_config with comprehensive config file"""
        logger = Logger(LogLevel.INFO)
        args = Namespace(log_level=None, log_format=None, max_warnings=None, ignore_dirs=None)
        config_path = tmp_path / "config.yaml"

        config_data = {
            "log_level": "DEBUG",
            "log_format": "yaml",
            "max_warnings": 20,
            "ignore_dirs": [".git", "build"],
            "code_snippet_max_lines": 5,
            "prompt_dirs": ["prompts"],
            "agent_dirs": ["agents"],
            "resource_dirs": ["refs"],
            "unreferenced_file_level": "WARNING",
            "missing_agents_file_level": "ERROR",
            "report_warning_threshold": 0.9,
            "prompt_max_tokens": 6000,
            "prompt_max_lines": 600,
            "agent_max_tokens": 7000,
            "agent_max_lines": 700,
            "enable_section_advices": False,
            "enable_section_mandatory": False,
            "missing_section_level": "ERROR",
            "mandatory_sections": ["testing"],
            "recommended_sections": ["architecture"],
        }
        config_path.write_text(yaml.dump(config_data))

        ignore_dirs, log_level, log_format, max_warnings, config = load_config(
            args, logger, str(config_path), LogLevel.INFO, LogFormat.FILE_DIGEST, [], -1
        )

        assert log_level == LogLevel.DEBUG
        assert log_format == LogFormat.YAML
        assert max_warnings == 20
        assert ignore_dirs == [".git", "build"]
        assert config.code_snippet_max_lines == 5
        assert config.prompt_dirs == ["prompts"]
        assert config.agent_dirs == ["agents"]
        assert config.resource_dirs == ["refs"]
        assert config.unreferenced_file_level == LogLevel.WARNING
        assert config.missing_agents_file_level == LogLevel.ERROR
        assert config.report_warning_threshold == 0.9
        assert config.prompt_max_tokens == 6000
        assert config.prompt_max_lines == 600
        assert config.agent_max_tokens == 7000
        assert config.agent_max_lines == 700
        assert config.enable_section_advices is False
        assert config.enable_section_mandatory is False
        assert config.missing_section_level == LogLevel.ERROR
        assert config.mandatory_sections == ["testing"]
        assert config.recommended_sections == ["architecture"]

    def test_load_config_invalid_yaml(self, tmp_path: Path) -> None:
        """Test load_config with invalid YAML"""
        logger = Logger(LogLevel.INFO)
        args = Namespace(log_level=None, log_format=None, max_warnings=None, ignore_dirs=None)
        config_path = tmp_path / "invalid.yaml"
        config_path.write_text("invalid: yaml: content:")

        ignore_dirs, log_level, log_format, max_warnings, config = load_config(
            args, logger, str(config_path), LogLevel.INFO, LogFormat.FILE_DIGEST, [], -1
        )

        # Should fallback to defaults
        assert log_level == LogLevel.INFO
        assert isinstance(config, Config)

    def test_load_config_non_dict_yaml(self, tmp_path: Path) -> None:
        """Test load_config with YAML that isn't a dictionary"""
        logger = Logger(LogLevel.INFO)
        args = Namespace(log_level=None, log_format=None, max_warnings=None, ignore_dirs=None)
        config_path = tmp_path / "list.yaml"
        config_path.write_text("- item1\n- item2")

        ignore_dirs, log_level, log_format, max_warnings, config = load_config(
            args, logger, str(config_path), LogLevel.INFO, LogFormat.FILE_DIGEST, [], -1
        )

        # Should fallback to defaults
        assert log_level == LogLevel.INFO
        assert isinstance(config, Config)
