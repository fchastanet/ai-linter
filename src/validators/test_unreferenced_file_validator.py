from pathlib import Path

import pytest

from lib.log import Logger, LogLevel
from validators.unreferenced_file_validator import UnreferencedFileValidator


class TestUnreferencedFileValidator:
    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def validator(self, logger: Logger) -> UnreferencedFileValidator:
        """Create a validator"""
        return UnreferencedFileValidator(logger, level="ERROR")

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
        md_file.write_text("[Link](references/test.txt)")

        warnings, errors = validator.validate_unreferenced_files(tmp_path, resource_dirs=["references"], ignore_dirs=[])

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
        md_file.write_text("# No references here")

        warnings, errors = validator.validate_unreferenced_files(tmp_path, resource_dirs=["references"], ignore_dirs=[])

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
        md_file.write_text("[Link](references/file.txt)")

        warnings, errors = validator.validate_unreferenced_files(
            tmp_path, resource_dirs=["references", "assets", "scripts"], ignore_dirs=[]
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
        md_file.write_text("[Link](../references/test.txt)")

        warnings, errors = validator.validate_unreferenced_files(tmp_path, resource_dirs=["references"], ignore_dirs=[])

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

        warnings, errors = validator.validate_unreferenced_files(
            tmp_path, resource_dirs=["references"], ignore_dirs=[".git"]
        )

        # Should not find any unreferenced files (ignored)
        assert warnings == 0
        assert errors == 0

    def test_warning_level(self, logger: Logger, tmp_path: Path) -> None:
        """Test validator with WARNING level"""
        validator = UnreferencedFileValidator(logger, level="WARNING")

        # Create unreferenced file
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        (ref_dir / "test.txt").write_text("content")

        md_file = tmp_path / "README.md"
        md_file.write_text("# No references")

        warnings, errors = validator.validate_unreferenced_files(tmp_path, resource_dirs=["references"], ignore_dirs=[])

        assert warnings == 1
        assert errors == 0
