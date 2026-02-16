from pathlib import Path

import pytest
import yaml

from lib.config import (
    DEFAULT_IGNORE_PATTERNS,
    Arguments,
    Config,
    get_log_level_from_string,
    load_config,
)
from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger


class TestConfig:
    """Test Config class functionality"""

    @pytest.fixture(autouse=True)
    def change_test_dir(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.chdir(tmp_path)

    @pytest.fixture
    def defaultArgs(self) -> Arguments:
        """Create an AiStats instance"""
        return Arguments(
            skills=False,
            directories=[],
            config_file=None,
            log_level=None,
            log_format=None,
            max_warnings=None,
            ignore=None,
        )

    def test_config_defaults(self) -> None:
        """Test that Config has expected default values"""
        config = Config()

        assert config.log_level == LogLevel.INFO
        assert config.log_format == LogFormat.FILE_DIGEST
        assert config.max_warnings == -1
        assert ".git" in config.ignore
        assert "__pycache__" in config.ignore
        assert config.code_snippet_max_lines == 3
        assert config.report_warning_threshold == 0.8
        assert config.unreferenced_file_level == LogLevel.ERROR
        assert config.missing_agents_file_level == LogLevel.WARNING

        # Test new defaults
        assert config.enable_mandatory_sections is True
        assert config.enable_advised_sections is True
        assert config.mandatory_sections_log_level == LogLevel.WARNING
        assert len(config.mandatory_sections) == 8
        assert "navigating the codebase" in config.mandatory_sections
        assert "build & commands" in config.mandatory_sections
        assert "security" in config.mandatory_sections
        assert len(config.advised_sections) == 4
        assert "git commit conventions" in config.advised_sections
        assert "architecture" in config.advised_sections

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

    def test_load_config_no_file(self, tmp_path: Path, defaultArgs: Arguments) -> None:
        """Test load_config when config file doesn't exist"""
        logger = Logger(LogLevel.INFO)
        config_path = str(tmp_path / "nonexistent.yaml")
        defaultArgs.config_file = config_path
        config = load_config(logger, defaultArgs, str(tmp_path))

        assert isinstance(config, Config)
        assert config.log_level == LogLevel.INFO
        assert config.log_format == LogFormat.FILE_DIGEST
        assert config.max_warnings == -1

    def test_load_config_empty_file(self, tmp_path: Path, defaultArgs: Arguments) -> None:
        """Test load_config with empty YAML file"""
        logger = Logger(LogLevel.INFO)

        config_path = tmp_path / "empty.yaml"
        config_path.write_text("")

        config = load_config(logger, defaultArgs, str(tmp_path))

        assert isinstance(config, Config)
        assert config.log_level == LogLevel.INFO
        assert config.log_format == LogFormat.FILE_DIGEST
        assert config.max_warnings == -1
        assert config.ignore == DEFAULT_IGNORE_PATTERNS
        assert config.code_snippet_max_lines == 3
        assert config.report_warning_threshold == 0.8
        assert config.unreferenced_file_level == LogLevel.ERROR
        assert config.missing_agents_file_level == LogLevel.WARNING
        assert config.enable_mandatory_sections is True
        assert config.enable_advised_sections is True

    def test_load_config_with_section_settings(self, tmp_path: Path, defaultArgs: Arguments) -> None:
        """Test load_config with section validation settings"""
        logger = Logger(LogLevel.INFO)
        args = defaultArgs
        config_path = tmp_path / "config.yaml"
        args.config_file = str(config_path)

        config_data = {
            "enable_mandatory_sections": False,
            "enable_advised_sections": False,
            "mandatory_sections_log_level": "ERROR",
            "mandatory_sections": ["Security", "Testing"],
            "advised_sections": ["Architecture", "Deployment"],
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(logger, args, str(tmp_path))

        assert config.enable_advised_sections is False
        assert config.enable_mandatory_sections is False
        assert config.mandatory_sections_log_level == LogLevel.ERROR
        assert config.mandatory_sections == {"security": "Security", "testing": "Testing"}
        assert config.advised_sections == {"architecture": "Architecture", "deployment": "Deployment"}

    def test_load_config_with_log_level(self, tmp_path: Path, defaultArgs: Arguments) -> None:
        """Test load_config with log level in config file"""
        logger = Logger(LogLevel.INFO)
        args = defaultArgs
        config_path = tmp_path / ".ai-linter-config.yaml"

        config_data = {"log_level": "WARNING"}
        config_path.write_text(yaml.dump(config_data))

        config = load_config(logger, args, str(tmp_path))

        assert config.log_level == LogLevel.WARNING

    def test_load_config_cli_overrides_file(self, tmp_path: Path, defaultArgs: Arguments) -> None:
        """Test that CLI arguments override config file"""
        logger = Logger(LogLevel.INFO)
        args = defaultArgs
        args.max_warnings = 5

        config_path = tmp_path / ".ai-linter-config.yaml"
        config_data = {
            "log_level": "WARNING",
            "max_warnings": 10,
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(logger, args, str(tmp_path))

        # CLI overrides file
        assert config.log_level == LogLevel.WARNING
        assert config.max_warnings == 5
        assert config.log_format == LogFormat.FILE_DIGEST
        assert config.ignore == [".git", "__pycache__"]
        assert config.code_snippet_max_lines == 3
        assert config.report_warning_threshold == 0.8
        assert config.unreferenced_file_level == LogLevel.ERROR

    def test_load_config_with_all_options(self, tmp_path: Path, defaultArgs: Arguments) -> None:
        """Test load_config with comprehensive config file"""
        logger = Logger(LogLevel.INFO)
        args = defaultArgs
        config_path = tmp_path / ".ai-linter-config.yaml"

        config_data = {
            "log_level": "DEBUG",
            "log_format": "yaml",
            "max_warnings": 20,
            "ignore": ["**/*.log", "build"],
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
            "enable_advised_sections": False,
            "enable_mandatory_sections": False,
            "mandatory_sections_log_level": "ERROR",
            "mandatory_sections": ["Testing"],
            "advised_sections": ["Architecture"],
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(logger, args, str(config_path))

        assert config.log_level == LogLevel.DEBUG
        assert config.log_format == LogFormat.YAML
        assert config.max_warnings == 20
        assert config.ignore == ["**/*.log", "build"]
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
        assert config.enable_advised_sections is False
        assert config.enable_mandatory_sections is False
        assert config.mandatory_sections_log_level == LogLevel.ERROR
        assert config.mandatory_sections == {"testing": "Testing"}
        assert config.advised_sections == {"architecture": "Architecture"}

    def test_load_config_invalid_yaml(self, tmp_path: Path, defaultArgs: Arguments) -> None:
        """Test load_config with invalid YAML"""
        logger = Logger(LogLevel.INFO)
        args = defaultArgs
        config_path = tmp_path / ".ai-linter-config.yaml"
        config_path.write_text("invalid: yaml: content:")

        config = load_config(logger, args, str(config_path))

        # Should fallback to defaults
        assert config.log_level == LogLevel.INFO
        assert isinstance(config, Config)

    def test_load_config_non_dict_yaml(self, tmp_path: Path, defaultArgs: Arguments) -> None:
        """Test load_config with YAML that isn't a dictionary"""
        logger = Logger(LogLevel.INFO)
        args = defaultArgs
        config_path = tmp_path / ".ai-linter-config.yaml"
        config_path.write_text("- item1\n- item2")

        config = load_config(logger, args, str(config_path))

        # Should fallback to defaults
        assert config.log_level == LogLevel.INFO
        assert isinstance(config, Config)

    def test_load_config_with_ignore_key(self, tmp_path: Path, defaultArgs: Arguments) -> None:
        """Test load_config with new 'ignore' key for glob patterns"""
        logger = Logger(LogLevel.INFO)
        args = defaultArgs
        config_path = tmp_path / ".ai-linter-config.yaml"
        config_data = {"ignore": ["**/*.log", "build", "*.egg-info"]}
        config_path.write_text(yaml.dump(config_data))

        config = load_config(logger, args, str(config_path))

        assert config.ignore == ["**/*.log", "build", "*.egg-info"]
