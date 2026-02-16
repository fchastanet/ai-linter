from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

import pytest

from lib.arguments import Arguments
from lib.config import Config
from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from processors.process_agents import ProcessAgents
from processors.process_projects import ProcessProjects
from processors.process_prompts import ProcessPrompts


class TestProcessProjects:
    """Test suite for ProcessProjects class"""

    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def parser(self, logger: Logger) -> Parser:
        """Create a parser"""
        return Parser(logger)

    @pytest.fixture
    def process_agents_mock(self) -> ProcessAgents:
        """Create a mock ProcessAgents"""
        mock = MagicMock(spec=ProcessAgents)
        mock.process_agents.return_value = (0, 0)
        return mock

    @pytest.fixture
    def process_prompts_mock(self) -> ProcessPrompts:
        """Create a mock ProcessPrompts"""
        mock = MagicMock(spec=ProcessPrompts)
        mock.process_sub_directories.return_value = (0, 0)
        return mock

    @pytest.fixture
    def processor(
        self, logger: Logger, parser: Parser, process_agents_mock: ProcessAgents, process_prompts_mock: ProcessPrompts
    ) -> ProcessProjects:
        """Create a ProcessProjects instance"""
        return ProcessProjects(logger, parser, process_agents_mock, process_prompts_mock)

    @pytest.fixture
    def config(self) -> Config:
        """Create a test config"""
        config = Config()
        config.ignore = []
        config.prompt_dirs = [".github/prompts"]
        config.agent_dirs = [".github/agents"]
        config.prompt_max_tokens = 5000
        config.prompt_max_lines = 500
        config.agent_max_tokens = 5000
        config.agent_max_lines = 500
        config.report_warning_threshold = 0.8
        return config

    @pytest.fixture
    def arguments(self) -> Arguments:
        """Create test arguments"""
        return Arguments(
            skills=False,
            directories=["."],
            config_file=None,
            log_level=LogLevel.INFO,
            log_format=LogFormat.FILE_DIGEST,
            max_warnings=10,
        )

    def test_process_projects_with_empty_directories(self, processor: ProcessProjects, arguments: Arguments) -> None:
        """Test processing with empty project directories"""
        project_dirs: set[str] = set()
        warnings, errors = processor.process_projects_for_directories(project_dirs, arguments)

        assert isinstance(warnings, int)
        assert isinstance(errors, int)
        assert warnings == 0
        assert errors == 0

    def test_process_projects_with_single_directory(self, processor: ProcessProjects, arguments: Arguments) -> None:
        """Test processing a single project directory"""
        with TemporaryDirectory() as tmpdir:
            project_dirs = {tmpdir}
            warnings, errors = processor.process_projects_for_directories(project_dirs, arguments)

            assert isinstance(warnings, int)
            assert isinstance(errors, int)
            # Should call process_agents and process_sub_directories
            processor.process_agents.process_agents.assert_called()  # type: ignore[attr-defined]

    def test_process_projects_with_multiple_directories(self, processor: ProcessProjects, arguments: Arguments) -> None:
        """Test processing multiple project directories"""
        with TemporaryDirectory() as tmpdir1:
            with TemporaryDirectory() as tmpdir2:
                project_dirs = {tmpdir1, tmpdir2}
                warnings, errors = processor.process_projects_for_directories(project_dirs, arguments)

                assert isinstance(warnings, int)
                assert isinstance(errors, int)

    def test_process_projects_ignores_patterns(self, processor: ProcessProjects, arguments: Arguments) -> None:
        """Test that ignored directories are skipped"""
        with TemporaryDirectory() as tmpdir:
            # Create a config with ignore patterns
            from unittest.mock import patch

            project_dirs = {tmpdir}
            with patch("processors.process_projects.load_config") as mock_load_config:
                config = Config()
                config.ignore = [tmpdir]  # Ignore this directory
                config.prompt_dirs = []
                config.agent_dirs = []
                mock_load_config.return_value = config

                warnings, errors = processor.process_projects_for_directories(project_dirs, arguments)

                # process_agents should not be called since the directory is ignored
                processor.process_agents.process_agents.assert_not_called()  # type: ignore[attr-defined]

    def test_process_projects_accumulates_warnings_and_errors(self, logger: Logger, parser: Parser) -> None:
        """Test that warnings and errors are accumulated correctly"""
        from unittest.mock import patch

        process_agents_mock = MagicMock(spec=ProcessAgents)
        process_agents_mock.process_agents.return_value = (2, 1)  # 2 warnings, 1 error

        process_prompts_mock = MagicMock(spec=ProcessPrompts)
        process_prompts_mock.process_sub_directories.return_value = (1, 0)  # 1 warning, 0 errors

        processor = ProcessProjects(logger, parser, process_agents_mock, process_prompts_mock)

        with TemporaryDirectory() as tmpdir:
            arguments = Arguments(
                skills=False,
                directories=[tmpdir],
                config_file=None,
                log_level=LogLevel.INFO,
                log_format=LogFormat.FILE_DIGEST,
                max_warnings=10,
            )

            with patch("processors.process_projects.load_config") as mock_load_config:
                config = Config()
                config.ignore = []
                config.prompt_dirs = [".github/prompts"]
                config.agent_dirs = [".github/agents"]
                config.prompt_max_tokens = 5000
                config.prompt_max_lines = 500
                config.agent_max_tokens = 5000
                config.agent_max_lines = 500
                config.report_warning_threshold = 0.8
                mock_load_config.return_value = config

                warnings, errors = processor.process_projects_for_directories({tmpdir}, arguments)

                # Should accumulate from all calls
                # process_agents: 2 warnings + 1 error
                # process_sub_directories (prompts): 1 warning + 0 errors
                # process_sub_directories (agents): 1 warning + 0 errors
                # Total should be at least 4 warnings and 1 error
                assert warnings >= 4
                assert errors >= 1
