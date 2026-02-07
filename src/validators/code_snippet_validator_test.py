from pathlib import Path

import pytest

from lib.log.log_level import LogLevel
from lib.log.logger import Logger
from validators.code_snippet_validator import CodeSnippetValidator


class TestCodeSnippetValidator:
    @pytest.fixture
    def logger(self) -> Logger:
        """Create a test logger"""
        return Logger(LogLevel.DEBUG)

    @pytest.fixture
    def validator(self, logger: Logger) -> CodeSnippetValidator:
        """Create a validator with max 3 lines"""
        return CodeSnippetValidator(logger, max_lines=3)

    def test_no_code_blocks(self, validator: CodeSnippetValidator, tmp_path: Path) -> None:
        """Test file with no code blocks"""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Header\n\nJust some text without code blocks.")

        warnings, errors = validator.validate_code_snippets(test_file, tmp_path, test_file.read_text())
        assert warnings == 0
        assert errors == 0

    def test_small_code_block(self, validator: CodeSnippetValidator, tmp_path: Path) -> None:
        """Test file with small code block (within limit)"""
        content = """# Test

```python
x = 1
y = 2
```
"""
        test_file = tmp_path / "test.md"
        test_file.write_text(content)

        warnings, errors = validator.validate_code_snippets(test_file, tmp_path, test_file.read_text())
        assert warnings == 0
        assert errors == 0

    def test_large_code_block(self, validator: CodeSnippetValidator, tmp_path: Path) -> None:
        """Test file with large code block (exceeds limit)"""
        content = """# Test

```python
x = 1
y = 2
z = 3
a = 4
b = 5
```
"""
        test_file = tmp_path / "test.md"
        test_file.write_text(content)

        warnings, errors = validator.validate_code_snippets(test_file, tmp_path, test_file.read_text())
        assert warnings == 1
        assert errors == 0

    def test_multiple_code_blocks(self, validator: CodeSnippetValidator, tmp_path: Path) -> None:
        """Test file with multiple code blocks"""
        content = """# Test

````python
x = 1
`````

Some text

````javascript
let a = 1;
let b = 2;
let c = 3;
let d = 4;
````
"""
        test_file = tmp_path / "test.md"
        test_file.write_text(content)

        warnings, errors = validator.validate_code_snippets(test_file, tmp_path, test_file.read_text())
        assert warnings == 1  # Only the large JavaScript block
        assert errors == 0

    def test_code_block_with_language(self, validator: CodeSnippetValidator, tmp_path: Path) -> None:
        """Test code block with language specifier"""
        content = """# Test

````typescript
const x: number = 1;
const y: string = "hello";
const z: boolean = true;
const a: any = null;
````

"""
        test_file = tmp_path / "test.md"
        test_file.write_text(content)

        warnings, errors = validator.validate_code_snippets(test_file, tmp_path, test_file.read_text())
        assert warnings == 1
        assert errors == 0

    def test_empty_lines_not_counted(self, validator: CodeSnippetValidator, tmp_path: Path) -> None:
        """Test that empty lines are not counted"""
        content = """# Test

````python
x = 1

y = 2

````
"""
        test_file = tmp_path / "test.md"
        test_file.write_text(content)

        warnings, errors = validator.validate_code_snippets(test_file, tmp_path, test_file.read_text())
        assert warnings == 0  # Only 2 non-empty lines
        assert errors == 0
