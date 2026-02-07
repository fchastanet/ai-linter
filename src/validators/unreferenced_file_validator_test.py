from pathlib import Path

import pytest

from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from validators.unreferenced_file_validator import UnreferencedFileValidator


class TestUnreferencedFileValidator:
    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def validator(self, logger: Logger) -> UnreferencedFileValidator:
        """Create a validator"""
        return UnreferencedFileValidator(logger)

    def test_extract_markdown_links(self, validator: UnreferencedFileValidator) -> None:
        """Test extracting markdown links"""
        content = """
# Test

[Link to file](path/to/file.txt)
![Image](images/test.png)
        """
        refs = validator.extract_file_references(content)
        assert "path/to/file.txt" in refs
        assert "images/test.png" in refs

    def test_extract_html_img_tags(self, validator: UnreferencedFileValidator) -> None:
        """Test extracting HTML img tags"""
        content = """
<img src="images/test.png" alt="Test">
<img src='another/image.jpg'>
        """
        refs = validator.extract_file_references(content)
        assert "images/test.png" in refs
        assert "another/image.jpg" in refs

    def test_extract_attachment_references(self, validator: UnreferencedFileValidator) -> None:
        """Test extracting attachment references"""
        content = """
<attachment filePath="path/to/document.pdf">
<attachment filePath='scripts/script.sh'>
        """
        refs = validator.extract_file_references(content)
        assert "path/to/document.pdf" in refs
        assert "scripts/script.sh" in refs

    def test_ignore_urls(self, validator: UnreferencedFileValidator) -> None:
        """Test that URLs are ignored"""
        content = """
[External](https://example.com)
<img src="http://example.com/image.png">
[Email](mailto:test@example.com)
        """
        refs = validator.extract_file_references(content)
        assert len(refs) == 0

    def test_referenced_files_ok(self, validator: UnreferencedFileValidator, tmp_path: Path) -> None:
        """Test that referenced files don't generate warnings"""
        # Create resource file
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        test_file = ref_dir / "test.txt"
        test_file.write_text("content")

        # Create markdown file referencing it
        md_file = tmp_path / "README.md"
        md_content = "[Link](references/test.txt)"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
        )

        assert warnings == 0
        assert errors == 0

    def test_referenced_files_ok_with_project_dir_different_from_relative_to(
        self, validator: UnreferencedFileValidator, tmp_path: Path
    ) -> None:
        """Test that referenced files don't generate warnings when project_dir is different from relative_to"""
        # Create project dir
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Create skill dir structure
        skill_dir = project_dir / "skill"
        skill_dir.mkdir()

        # Create resource file
        ref_dir = skill_dir / "references"
        ref_dir.mkdir()
        test_file = ref_dir / "test.txt"
        test_file.write_text("content")

        # Create markdown file referencing it
        md_file = skill_dir / "README.md"
        md_content = "[Link](references/test.txt)"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=skill_dir,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
        )

        assert warnings == 0
        assert errors == 0

    def test_unreferenced_file_detected(self, validator: UnreferencedFileValidator, tmp_path: Path) -> None:
        """Test that unreferenced files are detected"""
        # Create resource file without any references
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        test_file = ref_dir / "unreferenced.txt"
        test_file.write_text("content")

        # Create markdown file NOT referencing it
        md_file = tmp_path / "README.md"
        md_content = "# No references here"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
        )
        assert errors == 1  # Validator is set to ERROR level
        assert warnings == 0

    def test_unreferenced_file_detected_with_project_dir_different_from_relative_to(
        self, validator: UnreferencedFileValidator, tmp_path: Path
    ) -> None:
        """Test that unreferenced files are detected when project_dir is different from relative_to"""

        # Create project dir
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Create resource file without any references
        ref_dir = project_dir / "references"
        ref_dir.mkdir()
        test_file = ref_dir / "unreferenced.txt"
        test_file.write_text("content")

        # Create markdown file NOT referencing it
        md_file = project_dir / "README.md"
        md_content = "# No references here"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=project_dir,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
            level=LogLevel.ERROR,
        )
        assert errors == 1  # Validator is set to ERROR level
        assert warnings == 0

    def test_multiple_resource_dirs(self, validator: UnreferencedFileValidator, tmp_path: Path) -> None:
        """Test validation with multiple resource directories"""
        # Create multiple resource directories
        for dir_name in ["references", "assets", "scripts"]:
            dir_path = tmp_path / dir_name
            dir_path.mkdir()
            (dir_path / "file.txt").write_text("content")

        md_file = tmp_path / "README.md"
        md_content = "[Link](references/file.txt)"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("references"), Path("assets"), Path("scripts")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
        )

        # Should find 2 unreferenced files (in assets and scripts)
        assert errors == 2
        assert warnings == 0

    def test_relative_path_resolution(self, validator: UnreferencedFileValidator, tmp_path: Path) -> None:
        """Test that relative paths are resolved correctly"""
        # Create nested structure
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        test_file = ref_dir / "test.txt"
        test_file.write_text("content")

        # Create markdown file in docs/ referencing ../references/test.txt
        md_file = docs_dir / "guide.md"
        md_content = "[Link](../references/test.txt)"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
        )

        assert warnings == 0
        assert errors == 0

    def test_ignore_dirs(self, validator: UnreferencedFileValidator, tmp_path: Path) -> None:
        """Test that ignored directories are skipped"""
        # Create resource file in ignored directory
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        ignored = ref_dir / ".git"
        ignored.mkdir()
        (ignored / "file.txt").write_text("content")

        md_file = tmp_path / "README.md"
        md_content = "# No references"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[Path(".git")],
            level=LogLevel.ERROR,
        )

        # Should not find any unreferenced files (ignored)
        assert warnings == 0
        assert errors == 0

    def test_warning_level(self, logger: Logger, tmp_path: Path) -> None:
        """Test validator with WARNING level"""
        validator = UnreferencedFileValidator(logger)

        # Create unreferenced file
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        (ref_dir / "test.txt").write_text("content")

        md_file = tmp_path / "README.md"
        md_content = "# No references"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
            level=LogLevel.WARNING,
        )

        assert warnings == 1
        assert errors == 0

    def test_nested_markdown_references(self, validator: UnreferencedFileValidator, tmp_path: Path) -> None:
        """Test that references from nested markdown files are detected"""
        # Create resource files
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        (ref_dir / "main.txt").write_text("main content")
        (ref_dir / "nested.txt").write_text("nested content")

        # Create a nested markdown file
        nested_md = tmp_path / "docs.md"
        nested_md.write_text("[Link to nested](references/nested.txt)")

        # Create main markdown file referencing the nested markdown
        md_file = tmp_path / "README.md"
        md_content = "[Link to main](references/main.txt)\n[Nested doc](docs.md)"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
        )

        # Both files should be referenced
        assert warnings == 0
        assert errors == 0

    def test_nonexistent_resource_dir(self, validator: UnreferencedFileValidator, tmp_path: Path) -> None:
        """Test that nonexistent resource directories are handled gracefully"""
        md_file = tmp_path / "README.md"
        md_content = "# No references"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("nonexistent")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
        )

        # Should not error on missing directory
        assert warnings == 0
        assert errors == 0

    def test_markdown_reference_to_nonexistent_file(self, validator: UnreferencedFileValidator, tmp_path: Path) -> None:
        """Test that references to nonexistent markdown files are handled"""
        # Create resource file
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        (ref_dir / "test.txt").write_text("content")

        # Create main markdown file referencing nonexistent markdown
        md_file = tmp_path / "README.md"
        md_content = "[Link](references/test.txt)\n[Bad link](nonexistent.md)"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
        )

        # File is referenced, nonexistent markdown is silently ignored
        assert warnings == 0
        assert errors == 0

    def test_absolute_path_reference(self, validator: UnreferencedFileValidator, tmp_path: Path) -> None:
        """Test absolute path references from project root"""
        # Create resource file
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        (ref_dir / "test.txt").write_text("content")

        # Create markdown with absolute path reference
        md_file = tmp_path / "README.md"
        md_content = "[Link](/references/test.txt)"
        md_file.write_text(md_content)

        warnings, errors = validator.validate_unreferenced_files(
            project_dir=tmp_path,
            relative_to=tmp_path,
            resource_dirs=[Path("references")],
            markdown_content=md_content,
            markdown_file=md_file,
            ignore_dirs=[],
        )

        assert warnings == 0
        assert errors == 0
