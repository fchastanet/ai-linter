# AI Linter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![CI/CD](https://github.com/fchastanet/ai-linter/actions/workflows/ci.yml/badge.svg)](https://github.com/fchastanet/ai-linter/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/fchastanet/ai-linter/graph/badge.svg?token=V1IPNT3YFM)](https://codecov.io/github/fchastanet/ai-linter)

<!--TOC-->

- [1. Purpose](#1-purpose)
- [2. Features](#2-features)
- [3. Installation](#3-installation)
  - [3.1. From PyPI](#31-from-pypi)
  - [3.2. From Source](#32-from-source)
  - [3.3. Pre-commit Integration (Recommended)](#33-pre-commit-integration-recommended)
  - [3.4. Vscode Task Integration](#34-vscode-task-integration)
- [4. Command help](#4-command-help)
- [5. Usage](#5-usage)
  - [5.1. Basic Usage](#51-basic-usage)
  - [5.2. Advanced Options](#52-advanced-options)
  - [5.3. Configuration File](#53-configuration-file)
- [6. Validation Rules](#6-validation-rules)
  - [6.1. Code Snippet Size Validation](#61-code-snippet-size-validation)
  - [6.2. Unreferenced Resource File Detection](#62-unreferenced-resource-file-detection)
  - [6.3. Prompt and Agent Directory Validation](#63-prompt-and-agent-directory-validation)
  - [6.4. AGENTS.md Requirement](#64-agentsmd-requirement)
  - [6.5. Skills Validation](#65-skills-validation)
  - [6.6. Agents Validation](#66-agents-validation)
  - [6.7. Allowed Frontmatter Properties](#67-allowed-frontmatter-properties)
  - [6.8. Error Codes](#68-error-codes)
- [7. FAQ](#7-faq)
- [8. Exit Codes](#8-exit-codes)
- [9. Development](#9-development)
  - [9.1. Installation](#91-installation)
  - [9.2. Pre-commit](#92-pre-commit)
  - [9.3. Development Workflow](#93-development-workflow)
- [10. Inspiration](#10-inspiration)
- [11. Contributing](#11-contributing)
- [12. License](#12-license)

<!--TOC-->

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
- 📦 **Code Snippet Detection**: Warns about large code blocks that should be externalized
- 🔗 **Unreferenced File Detection**: Ensures all resource files are referenced in documentation
- 🤖 **Prompt/Agent Validation**: Validates `.github/prompts` and `.github/agents` directories
- 📄 **AGENTS.md Requirement**: Checks for project-level AI assistant guidance

## 3. Installation

### 3.1. From PyPI

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

### 3.3. Pre-commit Integration (Recommended)

See [.pre-commit-hooks.yaml](.pre-commit-hooks.yaml) for ready-to-use pre-commit hooks. Add to your
`.pre-commit-config.yaml`:

Lint entire workspace:

```yaml
repos:
  - repo: https://github.com/fchastanet/ai-linter
    rev: 0.3.3
    hooks:
      - id: ai-linter-workspace
        args: [--max-warnings, '5']
```

Lint entire workspace including skills:

```yaml
repos:
  - repo: https://github.com/fchastanet/ai-linter
    rev: 0.3.3
    hooks:
      - id: ai-linter-workspace
        args: [--skills, --max-warnings, '5']
```

Lint only changed files:

```yaml
repos:
  - repo: https://github.com/fchastanet/ai-linter
    rev: 0.3.3
    hooks:
      - id: ai-linter-changed-files
        args: [--max-warnings, '5']
```

### 3.4. Vscode Task Integration

Add the following task to your `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "AI Linter: Validate Workspace",
      "type": "shell",
      "command": "ai-linter",
      "args": [
        "--skills",
        "."
      ],
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "problemMatcher": {
        "owner": "ai-linter",
        "fileLocation": "absolute",
        "pattern": {
          "regexp": "^level=\"(WARNING|ERROR)\"\\s+rule=\"([^\"]+)\"\\s+path=\"([^\"]+)\"(?:\\s+line=\"(\\d+)\")?\\s+message=\"([^\"]+)\"",
          "file": 3,
          "line": 4,
          "severity": 1,
          "message": 5
        }
      }
    },
    {
      "label": "AI Linter: Validate Current Directory",
      "type": "shell",
      "command": "ai-linter",
      "args": [
        "--skills",
        "${workspaceFolder}"
      ],
      "group": {
        "kind": "test",
        "isDefault": false
      },
      "problemMatcher": {
        "owner": "ai-linter",
        "fileLocation": "absolute",
        "pattern": {
          "regexp": "^level=\"(WARNING|ERROR)\"\\s+rule=\"([^\"]+)\"\\s+path=\"([^\"]+)\"(?:\\s+line=\"(\\d+)\")?\\s+message=\"([^\"]+)\"",
          "file": 3,
          "line": 4,
          "severity": 1,
          "message": 5
        }
      }
    }
  ]
}
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

### 6.1. Code Snippet Size Validation

Code blocks in markdown files should not exceed a configurable line limit (default: 3 lines). Large code snippets should
be moved to external files and referenced from documentation.

**Configuration:**

```yaml
# .ai-linter-config.yaml
code_snippet_max_lines: 3  # Adjust as needed
```

**Example:**

```markdown
See the implementation in [process.py](scripts/process.py)
```

### 6.2. Unreferenced Resource File Detection

All files in `references/`, `assets/`, and `scripts/` directories must be referenced in at least one markdown file. This
prevents accumulation of unused files and ensures documentation stays synchronized with resources.

**Configuration:**

```yaml
resource_dirs:
  - references
  - assets
  - scripts
unreferenced_file_level: ERROR  # or WARNING, INFO
```

**Detection Methods:**

- Markdown links: `[text](path/to/file)`
- Images: `![alt](path/to/image.png)`
- HTML tags: `<img src="path">`
- Attachments: `<attachment filePath="path">`
- Code comments: `source: path/to/file`

### 6.3. Prompt and Agent Directory Validation

**Prompt and agent files are validated for:**

- Content size (≤ 500 lines)
- Token count (≤ 5000 tokens)
- All referenced files must exist
- Tool and skill references are extracted and logged

**Configuration:**

```yaml
prompt_dirs:
  - .github/prompts
agent_dirs:
  - .github/agents
```

### 6.4. AGENTS.md Requirement

Projects should have an `AGENTS.md` file in the root directory to provide AI assistants with project context and
guidance.

**Configuration:**

```yaml
missing_agents_file_level: WARNING  # or ERROR, INFO
```

### 6.5. Skills Validation

- `SKILL.md` file must exist
- Valid YAML frontmatter with required properties
- Content length ≤ 500 lines
- Token count ≤ 5000 tokens
- All file references must exist and be accessible
- Frontmatter must contain valid metadata

### 6.6. Agents Validation

- `AGENTS.md` file structure validation
- No frontmatter allowed in agent files
- Content length ≤ 500 lines
- Token count ≤ 5000 tokens
- All file references must be valid

### 6.7. Allowed Frontmatter Properties

```yaml
name: string
description: string
license: string
allowed-tools: array
metadata: object
compatibility: object
```

### 6.8. Error Codes

- `code-snippet-too-large`: Code block exceeds maximum line count
- `unreferenced-resource-file`: File in resource directory not referenced in any markdown
- `prompt-content-too-long`: File exceeds maximum line count
- `prompt-token-count-exceeded`: File exceeds maximum token count
- `agents-file-missing`: AGENTS.md not found in root directory

## 7. FAQ

- **Why limit code snippets to 3 lines?** This is configurable. The goal is to keep markdown focused on documentation
  while encouraging proper code organization in external files.
- **What if I have many small, rarely-used resource files?** Create an index document that lists all resources with
  their purposes. This satisfies the reference requirement and improves discoverability.
- **Can I disable specific validators?** Yes, set severity to `INFO` in config, or use `--ignore-dirs` to skip
  directories.
- **How are tokens counted?** Currently a simple whitespace split approximation. Actual AI tokenization may differ
  slightly. The limit provides a reasonable guideline.
- **Do I need AGENTS.md if my project is tiny?** Even small projects benefit from basic documentation. A minimal
  AGENTS.md can be just a few lines explaining the project's purpose.

## 8. Exit Codes

- **0**: Success (no errors, warnings within limits)
- **1**: Failure (errors found or too many warnings)

## 9. Development

### 9.1. Installation

```bash
# Clone and install for development
git clone git@github.com:fchastanet/ai-linter.git
cd ai-linter

# Install in development mode with all dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

### 9.2. Pre-commit

- ✅ **[.pre-commit-hooks.yaml](.pre-commit-hooks.yaml)** - Hook definitions for external use
- ✅ **[.pre-commit-config.yaml](.pre-commit-config.yaml)** - Local development configuration with:
  - AI Linter validation
  - Black code formatting
  - isort import sorting
  - flake8 linting
  - mypy type checking
  - bandit security scanning
  - YAML/Markdown validation

### 9.3. Development Workflow

```bash
# Setup development environment
make install-dev

# Run all checks
make check-all

# Test the linter
make validate
```

## 10. Inspiration

This tool was inspired by
[Anthropic's skill validation script](https://github.com/anthropics/skills/blob/ef740771ac901e03fbca3ce4e1c453a96010f30a/skills/skill-creator/scripts/quick_validate.py)
and adapted for broader AI development workflows.

## 11. Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 12. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
