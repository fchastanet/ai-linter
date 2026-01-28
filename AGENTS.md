# AI Linter Agent Configuration

This document describes the AI Linter project structure and provides guidance for AI agents working with this codebase.

## Project Overview

AI Linter is a specialized validation tool for AI skills and agent configurations.
It validates markdown files (`SKILL.md`, `AGENTS.md`) with specific formatting requirements,
frontmatter validation, content limits, and file reference checking.

## Project Structure

```text
ai-linter/
├── src/                          # Source code
│   ├── aiLinter.py              # Main entry point and CLI
│   ├── lib/                     # Core utilities
│   │   ├── config.py           # Configuration loading
│   │   ├── log.py              # Logging system
│   │   └── parser.py           # Content parsing utilities
│   ├── processors/             # Data processing modules
│   │   ├── process_agents.py   # Agent validation processing
│   │   └── process_skills.py   # Skill validation processing
│   └── validators/             # Validation logic
│       ├── agent_validator.py  # AGENTS.md validation
│       ├── skill_validator.py  # SKILL.md validation
│       ├── file_reference_validator.py # File existence checking
│       └── front_matter_validator.py   # YAML frontmatter validation
├── tests/                       # Test suite
├── examples/                    # Example files for testing
│   ├── sample-skill/           # Example skill directory
│   │   └── SKILL.md           # Example skill file
│   └── AGENTS.md              # Example agents file
├── .vscode/                    # VS Code configuration
│   ├── settings.json          # Editor settings
│   └── tasks.json             # Build and validation tasks
├── .github/                    # GitHub configuration
│   └── workflows/             # CI/CD pipelines
├── pyproject.toml             # Package configuration
├── Makefile                   # Development automation
├── .pre-commit-config.yaml    # Pre-commit hooks
├── .pre-commit-hooks.yaml     # Hook definitions for external use
└── docs/                      # Documentation files
    ├── README.md              # Main documentation
    ├── CONTRIBUTING.md        # Development guidelines
    ├── RELEASE.md             # Release procedures
    └── CHANGELOG.md           # Version history
```

## Key Components

### 1. Validators (`src/validators/`)

**Purpose**: Core validation logic for different file types

- **`skill_validator.py`**: Validates `SKILL.md` files
  - Frontmatter validation (YAML)
  - Content length limits (500 lines, 5000 tokens)
  - Required properties validation
  - File reference checking

- **`agent_validator.py`**: Validates `AGENTS.md` files
  - No frontmatter allowed
  - Content length limits
  - Token count validation

- **`file_reference_validator.py`**: Checks file existence
  - Validates that referenced files exist
  - Resolves relative paths correctly

- **`front_matter_validator.py`**: YAML frontmatter parsing
  - Validates YAML syntax
  - Checks required properties
  - Validates property types

### 2. Processors (`src/processors/`)

**Purpose**: Orchestrate validation workflows

- **`process_skills.py`**: Handles skill directory processing
- **`process_agents.py`**: Handles agent file processing

### 3. Core Library (`src/lib/`)

**Purpose**: Shared utilities and infrastructure

- **`config.py`**: Configuration file loading (.ai-linter-config.yaml)
- **`log.py`**: Structured logging with error codes
- **`parser.py`**: Content parsing utilities

## Command Line Interface

### Basic Commands

```bash
# Install the package
pip install -e ".[dev]"

# Validate skills in current directory
ai-linter --skills .

# Validate specific directory
ai-linter /path/to/directory

# Auto-discover skills in a directory
ai-linter --skills /path/to/skills/

# Show help
ai-linter --help

# Show version
ai-linter --version
```

### Advanced Usage

```bash
# Set log level for debugging
ai-linter --log-level DEBUG --skills .

# Limit warnings
ai-linter --max-warnings 5 --skills .

# Ignore specific directories
ai-linter --ignore-dirs node_modules build --skills .

# Use custom config file
ai-linter --config-file custom.yaml --skills .
```

### Development Commands

```bash
# Development setup
make install-dev
pre-commit install

# Code quality checks
make format          # Format with black & isort
make lint           # Run flake8 & mypy
make test           # Run pytest
make check-all      # Run all checks

# Package management
make clean          # Clean build artifacts
make build          # Build package
make upload         # Upload to PyPI

# Validation
make validate       # Run AI Linter on current directory
make validate-debug # Run with debug logging
```

## VS Code Integration

### Tasks Available

- **AI Linter: Validate Skills** - Validate current workspace
- **AI Linter: Validate Directory** - Validate specific directory
- **Python: Format with Black** - Code formatting
- **Python: Sort Imports (isort)** - Import organization
- **Python: Lint with Flake8** - Code linting
- **Python: Type Check (MyPy)** - Type checking
- **Python: Run Tests** - Execute test suite
- **Pre-commit: Run All Hooks** - Run all pre-commit checks
- **Build: Package** - Build distribution package
- **Build: Clean** - Clean build artifacts

### Running Tasks

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Tasks: Run Task"
3. Select desired task
4. View results in Problems panel

## Configuration

### Configuration File (.ai-linter-config.yaml)

```yaml
# Logging level
log_level: INFO  # DEBUG, INFO, WARNING, ERROR

# Maximum warnings before failure
max_warnings: 10

# Directories to ignore
ignore_dirs:
  - ".git"
  - "__pycache__"
  - "node_modules"
  - "build"
  - "dist"
  - ".vscode"
  - ".pytest_cache"
  - "venv"
  - "env"
```

## Validation Rules

### Skills Validation (`SKILL.md`)

**Required Structure:**

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
Content must be under 500 lines and 5000 tokens
```

**Validation Checks:**

- ✅ Frontmatter present and valid YAML
- ✅ Required properties: name, description
- ✅ Name format: hyphen-case (lowercase, hyphens, digits)
- ✅ Content length ≤ 500 lines
- ✅ Token count ≤ 5000 tokens
- ✅ File references exist
- ✅ Directory name matches skill name

### Agents Validation (`AGENTS.md`)

**Required Structure:**

```markdown
# Agent Configuration

Agent descriptions and configurations.
No frontmatter allowed.
```

**Validation Checks:**

- ✅ No frontmatter present
- ✅ Content length ≤ 500 lines
- ✅ Token count ≤ 5000 tokens
- ✅ File references exist

## Error Codes and Messages

### Common Error Codes

- **`skill-not-found`**: SKILL.md file missing
- **`invalid-frontmatter`**: YAML frontmatter syntax error
- **`required-property-missing`**: Missing required frontmatter property
- **`invalid-name-format`**: Name not in hyphen-case format
- **`name-directory-mismatch`**: Skill name doesn't match directory
- **`content-too-long`**: Content exceeds line limit
- **`token-count-exceeded`**: Content exceeds token limit
- **`file-reference-not-found`**: Referenced file doesn't exist
- **`agent-frontmatter-extracted`**: AGENTS.md contains frontmatter (not allowed)

### Log Levels

- **DEBUG**: Detailed execution information
- **INFO**: General information and progress
- **WARNING**: Issues that don't prevent execution
- **ERROR**: Critical errors that prevent validation

## Working with AI Agents

### For Code Analysis Agents

**Key Files to Understand:**

1. `src/aiLinter.py` - Main CLI and entry point
2. `src/validators/*.py` - Core validation logic
3. `src/**/*.test.py` - Each python file should have its associated unit test
4. `pyproject.toml` - Package configuration

**Common Tasks:**

- Adding new validation rules
- Modifying error messages
- Extending configuration options
- Adding new file type support

### For Documentation Agents

**Key Files to Maintain:**

1. `README.md` - User documentation
2. `CONTRIBUTING.md` - Development guide
3. `CHANGELOG.md` - Version history
4. `examples/` - Example files used as demonstration of this linter (contains intended linting errors)

**Documentation Standards:**

- Use clear, actionable language
- Include code examples
- Maintain version compatibility information
- Update examples when changing validation rules

### For Testing Agents

**Test Structure:**

- Unit tests in "src/**/*.test.py"
- CI/CD validation in `.github/workflows/`

**Testing Commands:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_ai_linter.py

# Run tests with verbose output
pytest -v
```

## Extension Points

### Adding New Validators

1. Create validator class in `src/validators/`
2. Implement validation logic
3. Add to main processing flow in `src/aiLinter.py`
4. Add configuration options if needed
5. Update documentation

### Adding New File Types

1. Create processor in `src/processors/`
2. Add command line option
3. Update argument parser
4. Add validation rules
5. Update documentation and examples

### Custom Error Handling

1. Add error codes to validators
2. Update logging in `src/lib/log.py`
3. Add problem matchers for VS Code integration
4. Update documentation

## Troubleshooting

### Common Issues

**Import Errors:**

```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

**Validation Failures:**

```bash
# Run with debug logging
ai-linter --log-level DEBUG --skills .
```

**VS Code Tasks Not Working:**

- Ensure package is installed: `pip install -e ".[dev]"`
- Check Python path in VS Code settings
- Reload VS Code window

**Pre-commit Issues:**

```bash
# Reinstall pre-commit hooks
pre-commit uninstall
pre-commit install
pre-commit run --all-files
```

This configuration enables AI agents to effectively understand and work with
the AI Linter codebase, whether for development, testing, documentation, or analysis tasks.
