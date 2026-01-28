# AI Linter

<!--TOC-->

- [1. Purpose](#1-purpose)
- [2. Features](#2-features)
- [3. Installation](#3-installation)
  - [3.1. From PyPI (Coming Soon)](#31-from-pypi-coming-soon)
  - [3.2. From Source](#32-from-source)
  - [3.3. Development Installation](#33-development-installation)
- [4. Command help](#4-command-help)
- [5. Usage](#5-usage)
  - [5.1. Basic Usage](#51-basic-usage)
  - [5.2. Advanced Options](#52-advanced-options)
  - [5.3. Configuration File](#53-configuration-file)
- [6. Validation Rules](#6-validation-rules)
  - [6.1. Skills Validation](#61-skills-validation)
  - [6.2. Agents Validation](#62-agents-validation)
  - [6.3. Allowed Frontmatter Properties](#63-allowed-frontmatter-properties)
  - [6.4. Pre-commit Integration](#64-pre-commit-integration)
- [7. Exit Codes](#7-exit-codes)
  - [7.1. Development Workflow](#71-development-workflow)
- [8. Inspiration](#8-inspiration)
- [9. Contributing](#9-contributing)
- [10. License](#10-license)

<!--TOC-->

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 1. Purpose

AI Linter is a validation tool specifically designed for AI skills and agent configurations. It provides comprehensive
linting and validation for:

- **AI Skills**: Validates `SKILL.md` files including frontmatter, content length, token count, and file references
- **AI Agents**: Validates `AGENTS.md` files and ensures proper structure without frontmatter
- **File References**: Checks that all referenced files exist and are accessible
- **Content Quality**: Enforces limits on content length and token counts to ensure optimal performance
- **Project Structure**: Validates overall project organization and file relationships

## 2. Features

- 🔍 **Comprehensive Validation**: Validates both skills and agents with detailed error reporting
- 📊 **Token Counting**: Uses tiktoken for accurate token count validation
- 📝 **Frontmatter Parsing**: Validates YAML frontmatter in skill files
- 🚫 **File Reference Checking**: Ensures all referenced files exist
- ⚙️ **Configurable**: Support for YAML configuration files
- 🎯 **Selective Processing**: Can process specific directories or auto-discover skills
- 📋 **Detailed Logging**: Multiple log levels with structured error reporting
- 🔧 **Pre-commit Integration**: Easy integration with pre-commit hooks

## 3. Installation

### 3.1. From PyPI (Coming Soon)

```bash
pip install ai-linter
```

### 3.2. From Source

```bash
# Clone the repository
git clone git@github.com:fchastanet/ai-linter.git
cd ai-linter

# Install the package
pip install .
```

### 3.3. Development Installation

```bash
# Clone and install for development
git clone git@github.com:fchastanet/ai-linter.git
cd ai-linter

# Install in development mode with all dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

## 4. Command help

```text
usage: aiLinter.py [-h]
          [--skills]
          [--max-warnings MAX_WARNINGS]
          [--ignore-dirs IGNORE_DIRS [IGNORE_DIRS ...]]
          [--log-level {ERROR,WARNING,INFO,DEBUG}]
          [--version]
          [--config-file CONFIG_FILE]
          directories [directories ...]

Quick validation script for skills

positional arguments:
  directories           Directories to validate

options:
  -h, --help            show this help message and exit
  --skills              Indicates that the input directories contain skills
  --max-warnings MAX_WARNINGS
                        Maximum number of warnings allowed before failing
  --ignore-dirs IGNORE_DIRS [IGNORE_DIRS ...]
                        List of directory patterns to ignore when validating AGENTS.md files
  --log-level {ERROR,WARNING,INFO,DEBUG}
                        Set the logging level
  --version             Show the version of the AI Linter
  --config-file CONFIG_FILE
                        Path to the AI Linter configuration file
```

## 5. Usage

After installation, you can use AI Linter via the `ai-linter` command or directly with Python.

### 5.1. Basic Usage

```bash
# Using the console script (recommended)
ai-linter /path/to/directory

# Auto-discover and validate all skills in a directory
ai-linter --skills /path/to/skills/directory

# Using the Python module directly
python src/aiLinter.py --skills examples/
```

### 5.2. Advanced Options

```bash
# Set maximum allowed warnings
ai-linter --max-warnings 5 /path/to/directory

# Ignore specific directories
ai-linter --ignore-dirs node_modules build /path/to/directory

# Set log level
ai-linter --log-level DEBUG /path/to/directory

# Use custom config file
ai-linter --config-file custom-config.yaml /path/to/directory

# Show version
ai-linter --version
```

### 5.3. Configuration File

Create a `.ai-linter-config.yaml` file in your project root:

```yaml
# Logging configuration
log_level: INFO  # DEBUG, INFO, WARNING, ERROR

# Maximum warnings before failing
max_warnings: 10

# Directories to ignore during validation
ignore_dirs:
  - .git
  - __pycache__
  - node_modules
  - build
  - dist
```

## 6. Validation Rules

### 6.1. Skills Validation

- ✅ `SKILL.md` file must exist
- ✅ Valid YAML frontmatter with required properties
- ✅ Content length must not exceed 500 lines
- ✅ Token count must not exceed 5000 tokens
- ✅ All file references must exist and be accessible
- ✅ Frontmatter must contain valid metadata

### 6.2. Agents Validation

- ✅ `AGENTS.md` file structure validation
- ✅ No frontmatter allowed in agent files
- ✅ Content length must not exceed 500 lines
- ✅ Token count must not exceed 5000 tokens
- ✅ All file references must be valid

### 6.3. Allowed Frontmatter Properties

```yaml
name: string
description: string
license: string
allowed-tools: array
metadata: object
compatibility: object
```

### 6.4. Pre-commit Integration

- ✅ **[.pre-commit-hooks.yaml](.pre-commit-hooks.yaml)** - Hook definitions for external use
- ✅ **[.pre-commit-config.yaml](.pre-commit-config.yaml)** - Local development configuration with:
  - AI Linter validation
  - Black code formatting
  - isort import sorting
  - flake8 linting
  - mypy type checking
  - bandit security scanning
  - YAML/Markdown validation

See [.pre-commit-hooks.yaml](.pre-commit-hooks.yaml) for ready-to-use pre-commit hooks. Add to your
`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/fchastanet/ai-linter
    rev: v0.1.0
    hooks:
      - id: ai-linter-skills
        args: [--max-warnings, '5']
```

## 7. Exit Codes

- **0**: Success (no errors, warnings within limits)
- **1**: Failure (errors found or too many warnings)

### 7.1. Development Workflow

```bash
# Setup development environment
make install-dev

# Run all checks
make check-all

# Test the linter
make validate
```

## 8. Inspiration

This tool was inspired by
[Anthropic's skill validation script](https://github.com/anthropics/skills/blob/ef740771ac901e03fbca3ce4e1c453a96010f30a/skills/skill-creator/scripts/quick_validate.py)
and adapted for broader AI development workflows.

## 9. Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 10. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
