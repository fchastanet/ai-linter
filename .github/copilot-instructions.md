# Copilot Instructions for AI Linter

This document provides comprehensive guidance for AI coding agents working with the AI Linter repository. Take time to
understand this file before making changes.

## 1. Table of Contents

- [2. Project Overview](#2-project-overview)
- [3. Technology Stack](#3-technology-stack)
- [4. Project Structure](#4-project-structure)
- [5. Getting Started](#5-getting-started)
- [6. Development Workflow](#6-development-workflow)
- [7. Testing](#7-testing)
- [8. Validation Rules](#8-validation-rules)
- [9. Common Issues & Workarounds](#9-common-issues--workarounds)
- [10. Code Style Guidelines](#10-code-style-guidelines)
- [11. Making Changes](#11-making-changes)
- [12. CI/CD Pipeline](#12-cicd-pipeline)
- [13. Troubleshooting](#13-troubleshooting)

## 2. Project Overview

**AI Linter** is a specialized validation tool for AI skills and agent configurations. It validates markdown files
(`SKILL.md`, `AGENTS.md`) with comprehensive checks including:

- YAML frontmatter validation (skills only)
- Content length and token count limits (500 lines, 5000 tokens)
- File reference validation (ensuring all referenced files exist)
- Code snippet size validation (warns about large code blocks)
- Unreferenced resource file detection
- Prompt/agent directory validation (`.github/prompts`, `.github/agents`)
- Project structure validation

**Key Purpose**: Ensure AI skills and agent configurations are properly formatted, maintainable, and optimized for token
usage.

## 3. Technology Stack

- **Language**: Python 3.10+ (supports 3.10, 3.11, 3.12)

- **Build System**: setuptools with setuptools_scm for versioning

- **Package Manager**: pip

- **Core Dependencies**:

  - `tiktoken>=0.5.0` - Token counting for AI models (cl100k_base encoding)
  - `PyYAML>=6.0` - YAML parsing
  - `pyparsing>=3.0.0` - Content parsing
  - `tabulate>=0.9.0` - Report formatting
  - `pathspec>=1.0.4` - Path pattern matching (gitignore-style)

- **Development Tools**:

  - `black` (line-length=120) - Code formatting
  - `isort` (profile=black) - Import sorting
  - `flake8` - Linting (max-line-length=120, ignore E203, W503)
  - `mypy` - Type checking (strict mode enabled)
  - `pytest` + `pytest-cov` - Testing with coverage
  - `pre-commit` - Git hooks automation

## 4. Project Structure

```text
ai-linter/
├── src/                          # Source code
│   ├── ai_linter.py              # Main entry point and CLI
│   ├── lib/                      # Core utilities
│   │   ├── config.py             # Configuration loading (.ai-linter-config.yaml)
│   │   ├── parser.py             # Markdown/YAML parsing
│   │   ├── ai/
│   │   │   └── stats.py          # Token counting (uses tiktoken)
│   │   ├── log/
│   │   │   ├── logger.py         # Structured logging
│   │   │   ├── formatters/       # Log formatters (file-digest, logfmt, yaml)
│   │   │   └── handlers.py       # Log handlers
│   │   └── filters/
│   │       └── file_filter.py    # File filtering (glob patterns)
│   ├── processors/               # Validation orchestration
│   │   ├── process_skills.py     # Skill processing pipeline
│   │   ├── process_agents.py     # Agent processing pipeline
│   │   └── process_prompts.py    # Prompt processing pipeline
│   └── validators/               # Validation logic (modular)
│       ├── skill_validator.py    # SKILL.md validation
│       ├── agent_validator.py    # AGENTS.md validation
│       ├── content_length_validator.py  # Line/token limits
│       ├── file_reference_validator.py  # File existence checks
│       ├── front_matter_validator.py    # YAML frontmatter
│       ├── code_snippet_validator.py    # Code block size checks
│       └── unreferenced_file_validator.py  # Resource file checks
├── tests/                        # Unit tests (mirror src/ structure)
├── examples/                     # Example files (intentionally contain errors)
│   ├── sample-skill/
│   │   └── SKILL.md
│   └── AGENTS.md
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                # Main CI/CD pipeline
│   │   └── precommit-autoupdate.yml
│   └── copilot-instructions.md   # This file
├── .vscode/
│   ├── settings.json             # Editor settings
│   └── tasks.json                # Build/validation tasks
├── pyproject.toml                # Package configuration
├── Makefile                      # Development automation
├── .ai-linter-config.yaml        # Linter configuration
├── .pre-commit-config.yaml       # Pre-commit hooks (local dev)
├── .pre-commit-hooks.yaml        # Hook definitions (for external use)
└── docs/
    ├── README.md
    ├── CONTRIBUTING.md
    ├── AGENTS.md                 # AI agent guidance (more detailed than this file)
    ├── RELEASE.md
    ├── CHANGELOG.md
    └── QUICK_REFERENCE.md
```

### 4.1. Key Architecture Patterns

- **Modular Validators**: Each validation rule is a separate class in `src/validators/`
- **Processor Pattern**: Orchestrators (`ProcessSkills`, `ProcessAgents`, `ProcessPrompts`) coordinate validators
- **Pluggable Logging**: Multiple formatters (file-digest, logfmt, yaml) for different use cases
- **Configuration Override**: CLI args > config file > defaults
- **Dependency Injection**: Components receive dependencies in constructors for testability

## 5. Getting Started

### 5.1. Installation

```bash
# Clone the repository
git clone https://github.com/fchastanet/ai-linter.git
cd ai-linter

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install in development mode
make install-dev
# This runs: pip install -e ".[dev]" && pre-commit install
```

**⚠️ Important**: Always use `make install-dev` instead of manual pip commands to ensure pre-commit hooks are installed.

### 5.2. Quick Validation

```bash
# Run AI Linter on current directory
make ai-linter
# or: ai-linter --skills .

# Debug mode (verbose output)
make ai-linter-debug
# or: ai-linter --log-level DEBUG --skills .

# Check version
ai-linter --version
```

## 6. Development Workflow

### 6.1. Code Formatting

```bash
# Format code (black + isort)
make format

# Check formatting without modifying files
black --line-length=120 --check src/
isort --profile black --check-only src/
```

**Auto-format on save**: Configured in `.vscode/settings.json` (use VS Code for best experience)

### 6.2. Linting

```bash
# Run all linting checks
make lint

# This runs:
# - black --check
# - isort --check
# - flake8 (max-line-length=120, ignore E203, W503)
# - mypy (type checking)
```

**Common Lint Fixes**:

- Import errors: Use `isort --profile black src/` to fix
- Line length: Black reformats automatically with `make format`
- Type errors: Add type hints or update `pyproject.toml` [tool.mypy] section

### 6.3. Testing

```bash
# Run tests with coverage
make test
# or: pytest --capture=sys --cov=src --cov-branch --cov-report=xml

# Run tests without coverage (faster)
pytest --no-cov

# Run specific test file
pytest src/validators/skill_validator_test.py

# Run tests matching pattern
pytest -k "test_skill_validator" --no-cov

# Stop at first failure (useful for debugging)
pytest -x --no-cov -vv
```

**Test Structure**:

- Each Python module should have a corresponding `*_test.py` file
- Tests use pytest conventions (`test_*` functions in `Test*` classes)
- Use fixtures for common setup (see existing tests)

### 6.4. Full Validation

```bash
# Run all checks (format + lint + test + ai-linter)
make check-all

# This is what CI runs - always pass this before committing
```

### 6.5. Pre-commit Hooks

```bash
# Install hooks (done automatically by make install-dev)
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

**Hooks Configured**:

- AI Linter validation
- Black formatting
- isort import sorting
- flake8 linting
- mypy type checking
- yamllint, markdownlint, mdformat
- bandit security scanning
- Git conflict checking

## 7. Testing

### 7.1. Running Tests

**⚠️ Network Dependency**: Tests that use tiktoken require internet access to download the `cl100k_base` encoding from
`openaipublic.blob.core.windows.net`. In restricted environments (CI, sandboxed), these tests may fail with
`ConnectionError`.

**Workaround**: Tests will pass once tiktoken encoding is cached locally. If tests fail due to network issues, this is
expected and not a code problem.

```bash
# Basic test run
make test

# Test with verbose output
pytest -v --no-cov

# Test with coverage report
pytest --cov=src --cov-report=html
# View report: open htmlcov/index.html
```

### 7.2. Writing Tests

**Guidelines**:

1. Follow existing test patterns (see `src/validators/*_test.py`)
2. Use descriptive test names: `test_<component>_<scenario>_<expected_outcome>`
3. Use fixtures for common setup (config, temporary files)
4. Test both success and failure cases
5. Mock external dependencies (file system, network)

**Example Test Structure**:

```python
import pytest
from pathlib import Path
from your_module import YourClass

class TestYourClass:
    @pytest.fixture
    def config(self):
        return {"max_warnings": 10, "log_level": "INFO"}

    def test_valid_input_returns_success(self, config):
        obj = YourClass(config)
        result = obj.validate("valid input")
        assert result.success is True

    def test_invalid_input_returns_error(self, config):
        obj = YourClass(config)
        result = obj.validate("invalid input")
        assert result.success is False
        assert "error-code" in result.errors
```

## 8. Validation Rules

### 8.1. Skills Validation (`SKILL.md`)

**Required Structure**:

```markdown
---
name: skill-name-in-hyphen-case
description: Brief description
license: MIT
allowed-tools:
  - tool1
  - tool2
metadata:
  author: Author Name
  version: "1.0.0"
compatibility:
  frameworks: ["anthropic", "openai"]
---

# Skill content here
```

**Validation Checks**:

- ✅ Frontmatter present and valid YAML
- ✅ Required properties: `name`, `description`
- ✅ Name format: hyphen-case (lowercase, hyphens, digits only)
- ✅ Directory name matches skill name
- ✅ Content ≤ 500 lines
- ✅ Token count ≤ 5000 tokens (cl100k_base encoding)
- ✅ All file references exist
- ✅ Code snippets ≤ 3 lines (configurable, warns if exceeded)

### 8.2. Agents Validation (`AGENTS.md`)

**Required Structure**:

```markdown
# Agent Configuration

Agent descriptions and configurations.
**No frontmatter allowed.**
```

**Validation Checks**:

- ✅ No frontmatter present (error if found)
- ✅ Content ≤ 500 lines (configurable: `agent_max_lines`)
- ✅ Token count ≤ 5000 tokens (configurable: `agent_max_tokens`)
- ✅ All file references exist
- ✅ Mandatory sections present (configurable: `mandatory_sections`)
  - Overview
  - Limitations
  - Navigating the Codebase
  - Build & Commands
  - Code Style
  - Testing
  - Security
  - Configuration

### 8.3. Common Error Codes

| Error Code                    | Description                     | Fix                                       |
| ----------------------------- | ------------------------------- | ----------------------------------------- |
| `skill-not-found`             | SKILL.md file missing           | Create SKILL.md in skill directory        |
| `invalid-frontmatter`         | YAML syntax error               | Fix YAML syntax (use yamllint)            |
| `required-property-missing`   | Missing `name` or `description` | Add required property to frontmatter      |
| `invalid-name-format`         | Name not in hyphen-case         | Use lowercase, hyphens, digits only       |
| `name-directory-mismatch`     | Skill name ≠ directory name     | Rename directory or update name           |
| `content-too-long`            | Exceeds line limit              | Split content or increase limit in config |
| `token-count-exceeded`        | Exceeds token limit             | Reduce content or externalize to files    |
| `file-reference-not-found`    | Referenced file doesn't exist   | Create file or fix path                   |
| `agent-frontmatter-extracted` | AGENTS.md has frontmatter       | Remove frontmatter (not allowed)          |
| `code-snippet-too-large`      | Code block > 3 lines            | Externalize to file or split              |

## 9. Common Issues & Workarounds

### 9.1. Issue 1: `tiktoken` Network Errors in Tests

**Symptom**: Tests fail with `ConnectionError: Failed to resolve 'openaipublic.blob.core.windows.net'`

**Cause**: tiktoken downloads encoding files on first use. Sandboxed/offline environments can't reach the server.

**Workaround**:

- Tests will pass once encoding is cached locally
- In CI, use a cached version or pre-download encodings
- Not a code bug - expected in restricted environments

**Example Error**:

```text
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='openaipublic.blob.core.windows.net', port=443):
Max retries exceeded with url: /encodings/cl100k_base.tiktoken
```

**Code Context**: This happens in `src/lib/ai/stats.py`:

```python
import tiktoken

def compute_token_count(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")  # Downloads on first use
    return len(encoding.encode(text))
```

### 9.2. Issue 2: Pre-commit Hook Failures

**Symptom**: `git commit` fails with validation errors

**Cause**: Pre-commit hooks run ai-linter and other checks automatically

**Workaround**:

```bash
# Fix issues first
make format    # Auto-format code
make lint      # Check for issues
make ai-linter # Validate AI files

# Or skip hooks temporarily (not recommended)
git commit --no-verify -m "message"
```

### 9.3. Issue 3: Import Errors After Installation

**Symptom**: `ModuleNotFoundError: No module named 'ai_linter'`

**Cause**: Package not installed or not in editable mode

**Workaround**:

```bash
# Reinstall in editable mode
pip uninstall ai-linter
make install-dev
```

### 9.4. Issue 4: `examples/` Validation Failures

**Symptom**: AI Linter reports errors in `examples/` directory

**Cause**: Examples intentionally contain errors for demonstration

**Workaround**:

- This is expected behavior
- Use `--ignore-dirs examples` to skip validation
- Or add `examples` to `ignore` list in `.ai-linter-config.yaml`

**Current Config**: `examples/` is NOT in the default ignore list, so validation will report errors.

### 9.5. Issue 5: Type Checking Errors with mypy

**Symptom**: `mypy` reports type errors

**Cause**: Missing type hints or incompatible types

**Workaround**:

1. Add type hints to function signatures

2. Update `pyproject.toml` [tool.mypy] to ignore specific imports:

   ```toml
   [tool.mypy]
   ignore_missing_imports = true
   ```

3. Use `# type: ignore` comments sparingly for third-party issues

## 10. Code Style Guidelines

### 10.1. General Python Style

- **Line Length**: 120 characters (configured in black/flake8)
- **Imports**: Sorted with isort (black profile)
- **Formatting**: Black (no manual formatting needed)
- **Type Hints**: Required for all function signatures (mypy strict mode)
- **Docstrings**: Use for public functions/classes (Google style preferred)

### 10.2. Naming Conventions

- **Modules**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_CASE_WITH_UNDERSCORES`
- **Private**: Prefix with `_single_underscore`

### 10.3. Import Organization (isort)

```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import tiktoken
import yaml

# Local application imports
from lib.config import Config
from validators.skill_validator import SkillValidator
```

### 10.4. Type Hints Example

```python
from typing import List, Dict, Optional, Tuple

def validate_skill(
    skill_path: Path,
    config: Dict[str, any],
    max_warnings: int = 10
) -> Tuple[bool, List[str]]:
    """Validate a skill directory.

    Args:
        skill_path: Path to skill directory
        config: Configuration dictionary
        max_warnings: Maximum warnings before failure

    Returns:
        Tuple of (success, error_messages)
    """
    errors: List[str] = []
    # Implementation
    return len(errors) == 0, errors
```

## 11. Making Changes

### 11.1. Before Making Changes

1. **Understand the issue**: Read the problem statement thoroughly
2. **Explore the code**: Use `view` or `grep` to understand affected areas
3. **Check existing tests**: Ensure you understand expected behavior
4. **Run tests**: `make test` to establish baseline
5. **Check current status**: `make check-all` to see if there are existing issues

### 11.2. Making Minimal Changes

**Guidelines**:

- Make the smallest possible change to fix the issue
- Don't refactor unrelated code
- Don't fix unrelated bugs or tests
- Update documentation only if directly related to your change
- Test your changes incrementally

### 11.3. Adding New Validators

1. Create validator class in `src/validators/`
2. Add corresponding test file `src/validators/your_validator_test.py`
3. Register validator in appropriate processor (`src/processors/`)
4. Add configuration options to `.ai-linter-config.yaml` if needed
5. Update `README.md` and `AGENTS.md` with validation rules
6. Run tests: `pytest src/validators/your_validator_test.py --no-cov`

### 11.4. Modifying Validation Rules

1. Locate validator in `src/validators/`
2. Update validation logic
3. Update corresponding tests
4. Update configuration schema in `src/lib/config.py`
5. Update documentation in `README.md`
6. Run full test suite: `make check-all`

### 11.5. Development Checklist

Before committing changes:

- [ ] Code formatted: `make format`
- [ ] Linting passes: `make lint`
- [ ] Tests pass: `make test`
- [ ] AI Linter passes: `make ai-linter`
- [ ] Documentation updated (if needed)
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] Full check passes: `make check-all`

## 12. CI/CD Pipeline

### 12.1. Workflow: `.github/workflows/ci.yml`

**Triggers**:

- Push to `master`, `develop` branches
- Pull requests to `master`
- Tags: `[0-9]+.[0-9]+.[0-9]+`
- Release: published
- Manual: `workflow_dispatch`

**Jobs**:

#### 12.1.1. Test Job (Matrix)

- **Python Versions**: 3.10, 3.11, 3.12
- **Steps**:
  1. Install dependencies: `make install` + `make install-dev`
  2. Run checks: `make check-all` (lint + test + ai-linter)
  3. Upload coverage to Codecov
  4. Run pre-commit hooks: `pre-commit-ci/lite-action`
- **Artifacts**: Coverage reports (`.coverage`, `coverage.xml`, `htmlcov/`)

#### 12.1.2. Build Job (on release/tag)

- **Steps**:
  1. Build package: `python -m build`
  2. Validate with twine: `twine check dist/*`
  3. Generate changelog
  4. Publish to PyPI

**⚠️ Note**: CI runs `make check-all` which includes:

- `make lint` - All linting checks
- `make test-all` - Tests + AI Linter validation
- Coverage reporting

### 12.2. Viewing CI Results

```bash
# Check CI status on GitHub
# https://github.com/fchastanet/ai-linter/actions

# Download coverage reports from artifacts
# Access via Actions tab > Workflow run > Artifacts
```

## 13. Troubleshooting

### 13.1. Debug Mode

```bash
# Run AI Linter with debug logging
ai-linter --log-level DEBUG --skills .

# Use different log format for machine parsing
ai-linter --log-format yaml --skills .
ai-linter --log-format logfmt --skills .
```

### 13.2. Common Commands

```bash
# Clean build artifacts
make clean

# Reinstall package
pip uninstall ai-linter
make install-dev

# Update dependencies
pip install --upgrade pip
pip install --upgrade -e ".[dev]"

# Run specific validator test
pytest -xvv src/validators/skill_validator_test.py::TestSkillValidator::test_valid_skill --no-cov

# Check configuration
ai-linter --help
```

### 13.3. Configuration File

`.ai-linter-config.yaml` controls all validation behavior:

```yaml
# Key settings
log_level: INFO                    # DEBUG, INFO, WARNING, ERROR
log_format: file-digest            # file-digest, logfmt, yaml
max_warnings: 10                   # -1 for unlimited
code_snippet_max_lines: 3          # Warn if code blocks exceed this
prompt_max_tokens: 5000            # Token limit for prompts
agent_max_tokens: 5000             # Token limit for agents
prompt_max_lines: 500              # Line limit for prompts
agent_max_lines: 500               # Line limit for agents
ignore:                            # Glob patterns to skip
  - .git
  - __pycache__
  - build/**
```

**CLI Override**: CLI arguments take precedence over config file

```bash
ai-linter --max-warnings 5 --log-level DEBUG --skills .
```

### 13.4. Getting Help

1. **README.md**: User-facing documentation
2. **CONTRIBUTING.md**: Development guidelines
3. **AGENTS.md**: Detailed AI agent guidance (more comprehensive than this file)
4. **QUICK_REFERENCE.md**: CLI quick reference
5. **Issue Tracker**: <https://github.com/fchastanet/ai-linter/issues>

### 13.5. Useful VS Code Tasks

Configured in `.vscode/tasks.json`:

- **AI Linter: Validate Workspace** - Run ai-linter on current directory
- **Python: Format with Black** - Format all Python files
- **Python: Run Tests** - Run pytest
- **Pre-commit: Run All Hooks** - Run all pre-commit checks

Access via: `Ctrl+Shift+P` → "Tasks: Run Task"

______________________________________________________________________

## 14. Quick Reference

### 14.1. Essential Commands

```bash
# Setup
make install-dev # Install for development

# Validation
make ai-linter       # Validate current directory
make ai-linter-debug # Validate with debug output

# Code Quality
make format    # Format code
make lint      # Run linting checks
make test      # Run tests
make check-all # Run all checks (CI equivalent)

# Cleanup
make clean # Remove build artifacts
```

### 14.2. Key Files to Know

- `src/ai_linter.py` - Main entry point, CLI handling
- `src/lib/config.py` - Configuration loading
- `src/processors/process_skills.py` - Skill validation orchestration
- `src/validators/*.py` - Individual validation rules
- `.ai-linter-config.yaml` - Linter configuration
- `pyproject.toml` - Package configuration
- `Makefile` - Development automation

### 14.3. Remember

- Always run `make check-all` before committing
- Use `make format` to auto-fix formatting issues
- Tests may fail with network errors (tiktoken) - this is expected
- Examples directory intentionally contains validation errors
- Pre-commit hooks run automatically - fix issues before committing
- Documentation updates are important for user-facing changes

______________________________________________________________________

**Last Updated**: 2026-02-12

For more detailed information, see:

- `README.md` - User documentation
- `AGENTS.md` - AI agent guidance (more comprehensive)
- `CONTRIBUTING.md` - Development workflow
