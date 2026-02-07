import tempfile
import unittest
from pathlib import Path

from lib.log import Logger, LogLevel
from validators.unreferenced_file_validator import UnreferencedFileValidator


class TestUnreferencedFileValidator(unittest.TestCase):
    """Tests for UnreferencedFileValidator"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.logger = Logger(LogLevel.ERROR)  # Use ERROR to suppress test output
        self.validator = UnreferencedFileValidator(self.logger)
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Clean up test fixtures"""
        # Clean up test directory
        import shutil

        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_import(self) -> None:
        """Test that validator can be imported"""
        from validators.unreferenced_file_validator import (  # noqa: F401
            UnreferencedFileValidator,
        )

        self.assertTrue(True, "Import successful")

    def test_no_directories(self) -> None:
        """Test with no assets/references/scripts directories"""
        skill_md = self.test_dir / "SKILL.md"
        skill_md.write_text("# Test\n\nNo files referenced")

        warnings, errors = self.validator.validate_unreferenced_files(self.test_dir, skill_md, skill_md.read_text())

        self.assertEqual(warnings, 0)
        self.assertEqual(errors, 0)

    def test_all_files_referenced(self) -> None:
        """Test when all files are referenced"""
        # Create directories and files
        (self.test_dir / "assets").mkdir()
        (self.test_dir / "assets" / "file1.txt").write_text("content")
        (self.test_dir / "references").mkdir()
        (self.test_dir / "references" / "doc.md").write_text("content")

        skill_md = self.test_dir / "SKILL.md"
        content = """# Test

Reference files:
- `assets/file1.txt`
- `references/doc.md`
"""
        skill_md.write_text(content)

        warnings, errors = self.validator.validate_unreferenced_files(self.test_dir, skill_md, content)

        self.assertEqual(warnings, 0)
        self.assertEqual(errors, 0)

    def test_unreferenced_files(self) -> None:
        """Test when files are not referenced"""
        # Create directories and files
        (self.test_dir / "assets").mkdir()
        (self.test_dir / "assets" / "referenced.txt").write_text("content")
        (self.test_dir / "assets" / "unreferenced.txt").write_text("content")
        (self.test_dir / "scripts").mkdir()
        (self.test_dir / "scripts" / "script.py").write_text("content")

        skill_md = self.test_dir / "SKILL.md"
        content = """# Test

Reference files:
- `assets/referenced.txt`
"""
        skill_md.write_text(content)

        warnings, errors = self.validator.validate_unreferenced_files(self.test_dir, skill_md, content)

        # Should have 2 warnings: assets/unreferenced.txt and scripts/script.py
        self.assertEqual(warnings, 2)
        self.assertEqual(errors, 0)

    def test_markdown_link_reference(self) -> None:
        """Test that markdown links are recognized as references"""
        # Create directories and files
        (self.test_dir / "assets").mkdir()
        (self.test_dir / "assets" / "image.png").write_text("content")

        skill_md = self.test_dir / "SKILL.md"
        content = """# Test

![Image](assets/image.png)
"""
        skill_md.write_text(content)

        warnings, errors = self.validator.validate_unreferenced_files(self.test_dir, skill_md, content)

        self.assertEqual(warnings, 0)
        self.assertEqual(errors, 0)

    def test_relative_path_reference(self) -> None:
        """Test that relative paths are normalized correctly"""
        # Create directories and files
        (self.test_dir / "assets").mkdir()
        (self.test_dir / "assets" / "file.txt").write_text("content")

        skill_md = self.test_dir / "SKILL.md"
        content = """# Test

Reference with relative path:
- `./assets/file.txt`
"""
        skill_md.write_text(content)

        warnings, errors = self.validator.validate_unreferenced_files(self.test_dir, skill_md, content)

        self.assertEqual(warnings, 0)
        self.assertEqual(errors, 0)

    def test_nested_directories(self) -> None:
        """Test files in nested directories"""
        # Create nested directories and files
        (self.test_dir / "assets" / "images").mkdir(parents=True)
        (self.test_dir / "assets" / "images" / "logo.png").write_text("content")
        (self.test_dir / "assets" / "images" / "icon.png").write_text("content")

        skill_md = self.test_dir / "SKILL.md"
        content = """# Test

Reference:
- `assets/images/logo.png`
"""
        skill_md.write_text(content)

        warnings, errors = self.validator.validate_unreferenced_files(self.test_dir, skill_md, content)

        # Should have 1 warning: assets/images/icon.png
        self.assertEqual(warnings, 1)
        self.assertEqual(errors, 0)

    def test_extract_file_references(self) -> None:
        """Test the file reference extraction method"""
        content = """# Test

Backtick references:
- `assets/file1.txt`
- `references/doc.md`

Markdown links:
- [Link](scripts/script.py)
- ![Image](assets/image.png)

Not file references:
- `some code`
- `variable_name`
"""

        references = self.validator._extract_file_references(content)

        # Should extract all file-like references
        self.assertIn("assets/file1.txt", references)
        self.assertIn("references/doc.md", references)
        self.assertIn("scripts/script.py", references)
        self.assertIn("assets/image.png", references)

        # Should not extract non-file references
        self.assertNotIn("some code", references)
        self.assertNotIn("variable_name", references)

    def test_normalize_path(self) -> None:
        """Test path normalization"""
        # Test removing leading ./
        self.assertEqual(self.validator._normalize_path("./assets/file.txt"), "assets/file.txt")

        # Test resolving ../
        self.assertEqual(self.validator._normalize_path("dir/../assets/file.txt"), "assets/file.txt")

        # Test multiple ../
        self.assertEqual(self.validator._normalize_path("dir1/dir2/../../assets/file.txt"), "assets/file.txt")


if __name__ == "__main__":
    unittest.main()
