from pathlib import Path

import pytest

from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from lib.parser import Parser
from validators.file_reference_validator import FileReferenceValidator


class TestFileReferenceValidator:
    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def parser(self, logger: Logger) -> Parser:
        """Create a parser"""
        return Parser(logger)

    @pytest.fixture
    def validator(self, logger: Logger, parser: Parser) -> FileReferenceValidator:
        """Create a FileReferenceValidator"""
        return FileReferenceValidator(logger, parser)

    def test_extract_markdown_links(self, validator: FileReferenceValidator) -> None:
        """Test extraction of markdown links"""
        content = "[link](path/to/file.txt)\n![image](images/photo.png)"
        references = validator._extract_file_references(content)
        assert "path/to/file.txt" in references
        assert "images/photo.png" in references

    def test_extract_backtick_paths(self, validator: FileReferenceValidator) -> None:
        """Test extraction of backtick-wrapped paths"""
        content = "See the file `docs/readme.md` for more info"
        references = validator._extract_file_references(content)
        assert "docs/readme.md" in references

    def test_extract_attachment_references(self, validator: FileReferenceValidator) -> None:
        """Test extraction of attachment file paths"""
        content = '<attachment filePath="path/to/attachment.pdf">'
        references = validator._extract_file_references(content)
        assert "path/to/attachment.pdf" in references

    def test_extract_agent_md_style_references(self, validator: FileReferenceValidator) -> None:
        """Test extraction of AGENTS.md style references"""
        content = "Refer to `@./resources/info.txt` for details or `@/absolute/path/to/info.txt`"
        references = validator._extract_file_references(content)
        assert "./resources/info.txt" in references
        assert "/absolute/path/to/info.txt" in references

    def test_ignore_external_urls(self, validator: FileReferenceValidator) -> None:
        """Test that external URLs are ignored"""
        content = "[external](https://example.com)\n[internal](docs/file.md)"
        references = validator._extract_file_references(content)
        assert "https://example.com" not in references
        assert "docs/file.md" in references

    def test_ignore_backtick_without_path(self, validator: FileReferenceValidator) -> None:
        """Test that backticks without paths are ignored"""
        content = "Here is a `code snippet` without a path"
        references = validator._extract_file_references(content)
        assert "code snippet" not in references

    def test_validate_resource_files_referenced_all_referenced(
        self, validator: FileReferenceValidator, tmp_path: Path
    ) -> None:
        """Test when all resource files are referenced"""
        # Create skill directory with resource files
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        ref_dir = skill_dir / "references"
        ref_dir.mkdir()
        (ref_dir / "file1.txt").write_text("content1")
        (ref_dir / "file2.txt").write_text("content2")

        # Create content that references both files
        content = "[link1](references/file1.txt)\n[link2](references/file2.txt)"

        md_file = skill_dir / "SKILL.md"
        # Pass skill_dir as base_dirs and "references" as resource_dirs
        warnings, errors = validator.validate_content_file_references(
            [skill_dir], md_file, content, 0, tmp_path, ["references"]
        )
        assert errors == 0
        assert warnings == 0

    def test_validate_resource_files_unreferenced(self, validator: FileReferenceValidator, tmp_path: Path) -> None:
        """Test detection of unreferenced resource files"""
        # Create skill directory with resource files
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        ref_dir = skill_dir / "references"
        ref_dir.mkdir()
        (ref_dir / "referenced.txt").write_text("content1")
        (ref_dir / "unreferenced.txt").write_text("content2")

        # Create content that only references one file
        content = "[link](references/referenced.txt)"

        md_file = skill_dir / "SKILL.md"
        warnings, errors = validator.validate_content_file_references(
            [skill_dir], md_file, content, 0, tmp_path, ["references"]
        )
        # Unreferenced files are warnings, not errors
        assert errors == 0
        assert warnings == 1

    def test_validate_resource_files_multiple_dirs(self, validator: FileReferenceValidator, tmp_path: Path) -> None:
        """Test validation with multiple resource directories"""
        # Create skill directory
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()

        # Create multiple resource directories
        docs_dir = skill_dir / "docs"
        docs_dir.mkdir()
        (docs_dir / "readme.md").write_text("readme")

        assets_dir = skill_dir / "assets"
        assets_dir.mkdir()
        (assets_dir / "logo.png").write_text("logo data")

        # Content references one file
        content = "[docs](docs/readme.md)"

        md_file = skill_dir / "SKILL.md"
        warnings, errors = validator.validate_content_file_references(
            [skill_dir], md_file, content, 0, tmp_path, ["docs", "assets"]
        )
        # Should report logo.png as unreferenced
        assert errors == 0
        assert warnings == 1

    def test_validate_content_file_references_valid(self, validator: FileReferenceValidator, tmp_path: Path) -> None:
        """Test validation of file references in content with valid references"""
        # Create a directory with target content
        sub_dir = tmp_path / "target"
        sub_dir.mkdir()
        test_file = sub_dir / "content.txt"
        test_file.write_text("target content")

        # Content with backtick reference to existing file
        md_file = tmp_path / "test.md"
        content = "See the file `target/content.txt` here"

        warnings, errors = validator.validate_content_file_references([tmp_path], md_file, content, 0, tmp_path, [])
        # Should not report errors for existing files that are referenced
        # File exists, so no error expected
        assert errors == 0

    def test_validate_content_file_references_invalid(self, validator: FileReferenceValidator, tmp_path: Path) -> None:
        """Test validation of file references in content with invalid references"""
        md_file = tmp_path / "test.md"
        content = "See the file `nonexistent/target.txt` here"

        warnings, errors = validator.validate_content_file_references([tmp_path], md_file, content, 0, tmp_path, [])
        # Should report error for non-existent file
        assert errors == 1

    def test_nested_resource_files(self, validator: FileReferenceValidator, tmp_path: Path) -> None:
        """Test validation with nested resource files"""
        # Create skill directory
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()

        # Create nested resource structure
        ref_dir = skill_dir / "references"
        ref_dir.mkdir()
        sub_dir = ref_dir / "sub"
        sub_dir.mkdir()
        (sub_dir / "nested.txt").write_text("nested content")

        # Content that references the nested file
        content = "[nested](references/sub/nested.txt)"

        md_file = skill_dir / "SKILL.md"
        warnings, errors = validator.validate_content_file_references(
            [skill_dir], md_file, content, 0, tmp_path, ["references"]
        )
        assert errors == 0
        assert warnings == 0
