"""Unit tests for ProcessPrompts"""

import tempfile
from pathlib import Path

from lib.ai.stats import AiStats
from lib.log.log_format import LogFormat
from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from processors.process_prompts import ProcessPrompts
from validators.content_length_validator import ContentLengthValidator
from validators.file_reference_validator import FileReferenceValidator


class TestProcessPrompts:
    """Test ProcessPrompts processor"""

    def test_process_markdown_file_valid(self) -> None:
        """Test processing a valid markdown file"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)
        parser = Parser(logger)
        ai_stats = AiStats(logger)
        content_validator = ContentLengthValidator(logger, ai_stats)
        file_ref_validator = FileReferenceValidator(logger, parser)

        processor = ProcessPrompts(logger, parser, content_validator, file_ref_validator)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.md"
            test_file.write_text("# Test\n\nThis is a test prompt.")

            warnings, errors = processor.process_markdown_file(
                test_file,
                temp_path,
                max_tokens=5000,
                max_lines=500,
                file_type="Prompt",
                warning_threshold=0.8,
            )

            assert errors == 0
            assert warnings == 0

    def test_process_markdown_file_too_long(self) -> None:
        """Test processing a markdown file that's too long"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)
        parser = Parser(logger)
        ai_stats = AiStats(logger)
        content_validator = ContentLengthValidator(logger, ai_stats)
        file_ref_validator = FileReferenceValidator(logger, parser)

        processor = ProcessPrompts(logger, parser, content_validator, file_ref_validator)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.md"
            # Create content with too many lines
            test_file.write_text("# Test\n\n" + ("Line\n" * 501))

            warnings, errors = processor.process_markdown_file(
                test_file,
                temp_path,
                max_tokens=5000,
                max_lines=500,
                file_type="Prompt",
                warning_threshold=0.8,
            )

            assert errors == 1
            assert warnings == 0

    def test_process_prompt_directories_no_dir(self) -> None:
        """Test processing when prompt directory doesn't exist"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)
        parser = Parser(logger)
        ai_stats = AiStats(logger)
        content_validator = ContentLengthValidator(logger, ai_stats)
        file_ref_validator = FileReferenceValidator(logger, parser)

        processor = ProcessPrompts(logger, parser, content_validator, file_ref_validator)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            warnings, errors = processor.process_sub_directories(
                temp_path,
                [],
                "Prompt",
                [".github/prompts"],
                max_tokens=5000,
                max_lines=500,
                warning_threshold=0.8,
            )

            assert warnings == 0
            assert errors == 0

    def test_process_prompt_directories_with_files(self) -> None:
        """Test processing prompt directories with files"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)
        parser = Parser(logger)
        ai_stats = AiStats(logger)
        content_validator = ContentLengthValidator(logger, ai_stats)
        file_ref_validator = FileReferenceValidator(logger, parser)

        processor = ProcessPrompts(logger, parser, content_validator, file_ref_validator)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            prompt_dir = temp_path / ".github" / "prompts"
            prompt_dir.mkdir(parents=True)

            # Create test prompt files
            (prompt_dir / "prompt1.md").write_text("# Prompt 1\n\nTest content")
            (prompt_dir / "prompt2.md").write_text("# Prompt 2\n\nTest content")

            warnings, errors = processor.process_sub_directories(
                temp_path,
                [],
                "Prompt",
                [".github/prompts"],
                max_tokens=5000,
                max_lines=500,
                warning_threshold=0.8,
            )

            # Should process both files successfully
            assert errors == 0
            assert warnings == 0

    def test_process_agent_directories_excludes_agents_md(self) -> None:
        """Test that AGENTS.md is excluded from agent directory processing"""
        logger = Logger(LogLevel.INFO, LogFormat.FILE_DIGEST)
        parser = Parser(logger)
        ai_stats = AiStats(logger)
        content_validator = ContentLengthValidator(logger, ai_stats)
        file_ref_validator = FileReferenceValidator(logger, parser)

        processor = ProcessPrompts(logger, parser, content_validator, file_ref_validator)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            agent_dir = temp_path / ".github" / "agents"
            agent_dir.mkdir(parents=True)

            # Create files
            (agent_dir / "AGENTS.md").write_text("# Agents\n\nShould be excluded")
            (agent_dir / "custom-agent.md").write_text("# Custom Agent\n\nTest content")

            warnings, errors = processor.process_sub_directories(
                temp_path,
                [],
                "Agent",
                [".github/agents"],
                max_tokens=5000,
                max_lines=500,
                warning_threshold=0.8,
            )
            assert errors == 0
            assert warnings == 0

            # Get report entries to verify only one file was processed
            entries = logger.get_report_entries()
            assert len(entries) == 1
            assert "custom-agent.md" in entries[0].file_path
