# AI Linter - Quick Reference Guide

<!--TOC-->

- [1. New Enhanced Features](#1-new-enhanced-features)
  - [1.1. Code Snippet Validation](#11-code-snippet-validation)
  - [1.2. Unreferenced File Detection](#12-unreferenced-file-detection)
  - [1.3. Prompt/Agent Validation](#13-promptagent-validation)
  - [1.4. AGENTS.md Requirement](#14-agentsmd-requirement)
- [2. Quick Start](#2-quick-start)
  - [2.1. Create/Update Config File](#21-createupdate-config-file)
  - [2.2. Run the Linter](#22-run-the-linter)
  - [2.3. Review Results](#23-review-results)
- [3. Common Use Cases](#3-common-use-cases)
  - [3.1. Reduce AI Context Size](#31-reduce-ai-context-size)
  - [3.2. Clean Up Resource Files](#32-clean-up-resource-files)
  - [3.3. Maintain Prompt Quality](#33-maintain-prompt-quality)
- [4. Error Codes Reference](#4-error-codes-reference)
- [5. Best Practices](#5-best-practices)
  - [5.1. ✅ DO](#51--do)
  - [5.2. ❌ DON'T](#52--dont)
- [6. Configuration Presets](#6-configuration-presets)
  - [6.1. Strict Mode (High Quality)](#61-strict-mode-high-quality)
  - [6.2. Balanced Mode (Recommended)](#62-balanced-mode-recommended)
  - [6.3. Lenient Mode (Large Projects)](#63-lenient-mode-large-projects)
- [7. Configuration Schema Reference](#7-configuration-schema-reference)
  - [7.1. Schema Overview](#71-schema-overview)
  - [7.2. Complete Property Reference](#72-complete-property-reference)
    - [7.2.1. Logging Configuration](#721-logging-configuration)
    - [7.2.2. General Validation Settings](#722-general-validation-settings)
    - [7.2.3. Content Limits](#723-content-limits)
    - [7.2.4. Directory Configuration](#724-directory-configuration)
    - [7.2.5. Validation Severity Levels](#725-validation-severity-levels)
    - [7.2.6. Section Validation Configuration](#726-section-validation-configuration)
    - [7.2.7. Report Configuration](#727-report-configuration)
  - [7.3. Validation Examples](#73-validation-examples)
- [8. Troubleshooting](#8-troubleshooting)
  - [8.1. Too Many Warnings](#81-too-many-warnings)
  - [8.2. False Positives](#82-false-positives)
  - [8.3. Configuration Not Loading](#83-configuration-not-loading)
- [9. Integration Examples](#9-integration-examples)
  - [9.1. Pre-commit Hook](#91-pre-commit-hook)
  - [9.2. GitHub Actions](#92-github-actions)
  - [9.3. Makefile](#93-makefile)
- [10. Resources](#10-resources)
- [11. Quick Commands](#11-quick-commands)

<!--TOC-->

## 1. New Enhanced Features

### 1.1. Code Snippet Validation

**What**: Detects oversized code blocks in markdown files

**Why**: Large code snippets bloat AI context; external files are more maintainable

**Default Limit**: 3 lines (configurable)

**Example Warning**:

```text
⚠️  Code snippet at line 68 has 25 lines (max: 3)
    Consider externalizing to an external file
```

**Configuration**:

```yaml
code_snippet_max_lines: 3  # Adjust to your preference
```

### 1.2. Unreferenced File Detection

**What**: Finds files in resource directories not referenced in any markdown

**Why**: Prevents accumulation of unused files; ensures documentation sync

**Default Directories**: `references/`, `assets/`, `scripts/`

**Example Error**:

```text
❌ File 'scripts/unused.sh' not referenced in any markdown file
```

**Configuration**:

```yaml
resource_dirs:
  - references
  - assets
  - scripts
unreferenced_file_level: ERROR  # or WARNING, INFO
```

### 1.3. Prompt/Agent Validation

**What**: Validates files in `.github/prompts` and `.github/agents`

**Why**: Ensures prompt quality, proper references, and reasonable token counts

**Checks**:

- Token count < 5000
- Line count < 500
- File references valid
- Tools and skills extraction

**Example Warning**:

```text
⚠️  Prompt has 6500 tokens (max: 5000)
    Consider splitting into multiple files
```

**Configuration**:

```yaml
prompt_dirs:
  - .github/prompts
agent_dirs:
  - .github/agents
```

### 1.4. AGENTS.md Requirement

**What**: Checks for AGENTS.md in project root

**Why**: AI assistants need project context and guidance

**Default**: WARNING (configurable to ERROR or INFO)

**Example Warning**:

```text
⚠️  AGENTS.md missing in root directory
    Consider creating one for AI assistant guidance
```

**Configuration**:

```yaml
missing_agents_file_level: WARNING  # or ERROR, INFO
```

## 2. Quick Start

### 2.1. Create/Update Config File

`.ai-linter-config.yaml`:

```yaml
log_level: INFO
max_warnings: 10
code_snippet_max_lines: 3
resource_dirs: [references, assets, scripts]
unreferenced_file_level: ERROR
missing_agents_file_level: WARNING
```

### 2.2. Run the Linter

```bash
# Validate current directory
ai-linter .

# Validate skills
ai-linter --skills .

# With debug output
ai-linter . --log-level DEBUG
```

### 2.3. Review Results

```text
Total warnings: 15, Total errors: 2
```

Exit code:

- `0` = Success (no errors, warnings ≤ max)
- `1` = Failure (errors > 0 or warnings > max)

## 3. Common Use Cases

### 3.1. Reduce AI Context Size

**Problem**: AI context getting too large with embedded code

**Solution**: Use code snippet validation

```yaml
code_snippet_max_lines: 3  # Strict
```

**Fix**:

- Extract code to files in `scripts/` or `references/`
- Link using markdown: `[script](scripts/example.sh)`

### 3.2. Clean Up Resource Files

**Problem**: Accumulating unused files in resource directories

**Solution**: Use unreferenced file detection

```yaml
unreferenced_file_level: ERROR
```

**Fix**:

- Add references in markdown documentation
- Remove truly unused files
- Move internal files out of resource directories

### 3.3. Maintain Prompt Quality

**Problem**: Prompts getting too long and unfocused

**Solution**: Use prompt/agent validation

**Fix**:

- Split large prompts into:
  - Main prompt (core instructions)
  - Reference documents
  - Separate skills
- Keep each under 5000 tokens

## 4. Error Codes Reference

| Code                          | Level              | Description                     |
| ----------------------------- | ------------------ | ------------------------------- |
| `code-snippet-too-large`      | WARNING            | Code block exceeds max lines    |
| `unreferenced-resource-file`  | ERROR/WARNING/INFO | File not referenced in markdown |
| `prompt-content-too-long`     | WARNING            | Prompt exceeds 500 lines        |
| `prompt-token-count-exceeded` | WARNING            | Prompt exceeds 5000 tokens      |
| `agents-file-missing`         | WARNING/ERROR/INFO | AGENTS.md not found             |
| `tools-found`                 | INFO               | Tool references detected        |
| `skills-found`                | INFO               | Skill references detected       |

## 5. Best Practices

### 5.1. ✅ DO

- Keep code snippets minimal (≤3 lines)
- Reference all resource files in documentation
- Split large prompts into modular pieces
- Create and maintain AGENTS.md
- Use configuration file for project standards
- Run linter in pre-commit hooks

### 5.2. ❌ DON'T

- Embed large code blocks in markdown
- Accumulate unused resource files
- Create 1000+ line prompt files
- Skip AGENTS.md for non-trivial projects
- Ignore linter warnings without review

## 6. Configuration Presets

### 6.1. Strict Mode (High Quality)

```yaml
log_level: INFO
max_warnings: 0
code_snippet_max_lines: 3
unreferenced_file_level: ERROR
missing_agents_file_level: ERROR
```

### 6.2. Balanced Mode (Recommended)

```yaml
log_level: INFO
max_warnings: 10
code_snippet_max_lines: 5
unreferenced_file_level: ERROR
missing_agents_file_level: WARNING
```

### 6.3. Lenient Mode (Large Projects)

```yaml
log_level: WARNING
max_warnings: 50
code_snippet_max_lines: 10
unreferenced_file_level: WARNING
missing_agents_file_level: INFO
```

## 7. Configuration Schema Reference

The `.ai-linter-config.yaml` file follows a JSON Schema that validates all configuration properties. See
`schemas/ai-linter-config.schema.json` for the complete schema definition.

### 7.1. Schema Overview

| Property                       | Category        | Type    | Range                       | Default                       | Validation                          |
| ------------------------------ | --------------- | ------- | --------------------------- | ----------------------------- | ----------------------------------- |
| `log_level`                    | Logging         | enum    | DEBUG\|INFO\|WARNING\|ERROR | INFO                          | String enum                         |
| `log_format`                   | Logging         | enum    | file-digest\|logfmt\|yaml   | file-digest                   | String enum                         |
| `unreferenced_file_level`      | Severity Levels | enum    | ERROR\|WARNING\|INFO        | ERROR                         | String enum                         |
| `missing_agents_file_level`    | Severity Levels | enum    | ERROR\|WARNING\|INFO        | WARNING                       | String enum                         |
| `mandatory_sections_log_level` | Severity Levels | enum    | ERROR\|WARNING              | WARNING                       | String enum (ERROR or WARNING only) |
| `max_warnings`                 | Validation      | integer | -1 to max int               | -1                            | -1 for unlimited                    |
| `ignore`                       | Validation      | array   | -                           | \[.git, **pycache**\]         | List of glob strings                |
| `code_snippet_max_lines`       | Content Limits  | integer | 1+                          | 3                             | Positive integer                    |
| `skill_max_tokens`             | Content Limits  | integer | 1+                          | 5000                          | Positive integer                    |
| `skill_max_lines`              | Content Limits  | integer | 1+                          | 500                           | Positive integer                    |
| `prompt_max_tokens`            | Content Limits  | integer | 1+                          | 5000                          | Positive integer                    |
| `prompt_max_lines`             | Content Limits  | integer | 1+                          | 500                           | Positive integer                    |
| `agent_max_tokens`             | Content Limits  | integer | 1+                          | 5000                          | Positive integer                    |
| `agent_max_lines`              | Content Limits  | integer | 1+                          | 500                           | Positive integer                    |
| `prompt_dirs`                  | Directories     | array   | -                           | [.github/prompts]             | List of directory paths             |
| `agent_dirs`                   | Directories     | array   | -                           | [.github/agents]              | List of directory paths             |
| `resource_dirs`                | Directories     | array   | -                           | [references, assets, scripts] | List of directory paths             |
| `report_warning_threshold`     | Reporting       | number  | 0.0-1.0                     | 0.8                           | Float between 0 and 1               |
| `enable_mandatory_sections`    | Sections        | boolean | true\|false                 | true                          | Boolean                             |
| `mandatory_sections`           | Sections        | array   | -                           | 8 default sections            | List of strings                     |
| `enable_advised_sections`      | Sections        | boolean | true\|false                 | true                          | Boolean                             |
| `advised_sections`             | Sections        | array   | -                           | 4 default sections            | List of strings                     |

Property types are grouped by category:

- **Logging**: Control output verbosity and format
- **Validation**: Set validation thresholds and exclusions
- **Content Limits**: Define size constraints
- **Directories**: Specify validation targets
- **Severity Levels**: Configure error reporting
- **Section Validation**: Manage AGENTS.md sections
- **Reporting**: Set warning thresholds for reports

### 7.2. Complete Property Reference

#### 7.2.1. Logging Configuration

```yaml
log_level: INFO                    # DEBUG | INFO | WARNING | ERROR
log_format: file-digest            # file-digest | logfmt | yaml
```

**Details:**

- `log_level`: Controls output verbosity
  - `DEBUG`: Detailed execution information
  - `INFO`: General information and progress (default)
  - `WARNING`: Issues that don't prevent execution
  - `ERROR`: Critical errors that prevent validation
- `log_format`: Controls how logs are formatted
  - `file-digest`: Human-readable format grouped by file (default)
  - `logfmt`: Key=value pairs on each line
  - `yaml`: Structured YAML output (machine-readable)

#### 7.2.2. General Validation Settings

```yaml
max_warnings: 10                   # integer (-1 = unlimited)
ignore: [.git, __pycache__]        # list of glob patterns
```

**Details:**

- `max_warnings`: Linter fails if warnings exceed this number. Use `-1` for unlimited
- `ignore`: Glob patterns to skip validation
  - Supports `*`, `?`, `[seq]`, `[!seq]`
  - Applied to both files and directories
  - Examples: `.git`, `__pycache__`, `node_modules`, `build/**`, `*.egg-info`

#### 7.2.3. Content Limits

```yaml
code_snippet_max_lines: 3          # lines (1-255)
skill_max_tokens: 5000             # tokens
skill_max_lines: 500               # lines
prompt_max_tokens: 5000            # tokens
prompt_max_lines: 500              # lines
agent_max_tokens: 5000             # tokens
agent_max_lines: 500               # lines
```

**Details:**

- `code_snippet_max_lines`: Warns if code blocks in markdown exceed this size. Prevents bloated AI context
- `skill_max_tokens`: Validates skill files don't exceed token count (OpenAI's cl100k_base encoding)
- `skill_max_lines`: Validates skill files don't exceed line count
- `prompt_max_tokens`: Validates files in `prompt_dirs` don't exceed token count (OpenAI's cl100k_base encoding)
- `prompt_max_lines`: Validates files in `prompt_dirs` don't exceed line count
- `agent_max_tokens`: Validates files in `agent_dirs` don't exceed token count
- `agent_max_lines`: Validates files in `agent_dirs` don't exceed line count

#### 7.2.4. Directory Configuration

```yaml
prompt_dirs: [.github/prompts]     # list of paths
agent_dirs: [.github/agents]       # list of paths
resource_dirs: [references, assets, scripts]  # list of paths
```

**Details:**

- `prompt_dirs`: Directories to validate for prompt quality
- `agent_dirs`: Directories to validate for agent configuration
- `resource_dirs`: Directories that should have all files referenced in markdown

#### 7.2.5. Validation Severity Levels

```yaml
unreferenced_file_level: ERROR     # ERROR | WARNING | INFO
missing_agents_file_level: WARNING  # ERROR | WARNING | INFO
mandatory_sections_log_level: WARNING # ERROR | WARNING (only)
```

**Details:**

- `unreferenced_file_level`: How to handle files in `resource_dirs` not referenced in markdown
- `missing_agents_file_level`: How to handle missing AGENTS.md file in project root
- `mandatory_sections_log_level`: How to handle missing mandatory sections in AGENTS.md

#### 7.2.6. Section Validation Configuration

```yaml
enable_mandatory_sections: true    # boolean
mandatory_sections:                # list of strings
  - Overview
  - Limitations
  - Navigating the Codebase
  - Build & Commands
  - Code Style
  - Testing
  - Security
  - Configuration

enable_advised_sections: true      # boolean
advised_sections:                  # list of strings
  - Architecture
  - Build Process
  - Git Commit Conventions
  - Troubleshooting
```

**Details:**

- `enable_mandatory_sections`: Enable checks for required sections in AGENTS.md
- `mandatory_sections`: Sections that MUST be present (case-insensitive matching)
- `enable_advised_sections`: Enable recommendations for additional sections
- `advised_sections`: Sections SHOULD be present but don't cause errors

#### 7.2.7. Report Configuration

```yaml
report_warning_threshold: 0.8      # 0.0-1.0 (0.8 = 80%)
```

**Details:**

- `report_warning_threshold`: Percentage of limit that triggers a warning. Used for content length reporting
  - `0.8` (default): Files at 80% of limit show warning
  - Lower values = earlier warnings (e.g., 0.5 = 50%)
  - Higher values = later warnings (e.g., 0.95 = 95%)

### 7.3. Validation Examples

**Minimal Config (uses all defaults):**

```yaml
log_level: INFO
```

**Custom Directories:**

```yaml
prompt_dirs:
  - .github/prompts
  - docs/prompts
  - src/prompts
agent_dirs:
  - .github/agents
  - docs/agents
resource_dirs:
  - references
  - assets
  - scripts
  - examples
```

**Strict Quality Control:**

```yaml
log_level: INFO
max_warnings: 0
code_snippet_max_lines: 2
prompt_max_tokens: 3000
prompt_max_lines: 300
agent_max_tokens: 3000
agent_max_lines: 300
unreferenced_file_level: ERROR
missing_agents_file_level: ERROR
mandatory_sections_log_level: ERROR
```

**Large Enterprise Setup:**

```yaml
log_level: WARNING
max_warnings: 100
code_snippet_max_lines: 10
prompt_max_tokens: 8000
prompt_max_lines: 800
agent_max_tokens: 8000
agent_max_lines: 800
ignore:
  - .git
  - __pycache__
  - node_modules
  - build/**
  - dist/**
  - .vscode
  - .pytest_cache
  - venv
  - env
  - .history
  - doc/**
  - examples/**
unreferenced_file_level: WARNING
missing_agents_file_level: INFO
```

## 8. Troubleshooting

### 8.1. Too Many Warnings

**Problem**: Linter fails with too many warnings

**Solution**:

1. Increase `max_warnings` temporarily
2. Fix issues incrementally
3. Lower back to desired threshold

### 8.2. False Positives

**Problem**: File flagged as unreferenced but it is referenced

**Solution**:

1. Check reference format (relative paths)
2. Ensure reference in markdown link: `[text](path)`
3. Verify file path is correct

### 8.3. Configuration Not Loading

**Problem**: Changes to config file not reflected

**Solution**:

1. Verify file is `.ai-linter-config.yaml`
2. Check file is in project root or specified with `--config-file`
3. Validate YAML syntax

## 9. Integration Examples

### 9.1. Pre-commit Hook

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: ai-linter
        name: AI Linter
        entry: ai-linter
        args: [.]
        language: python
        pass_filenames: false
```

### 9.2. GitHub Actions

`.github/workflows/lint.yml`:

```yaml
name: AI Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install ai-linter
      - run: ai-linter .
```

### 9.3. Makefile

```makefile
.PHONY: lint
lint:
 ai-linter .

.PHONY: lint-strict
lint-strict:
 ai-linter . --max-warnings 0

.PHONY: lint-debug
lint-debug:
 ai-linter . --log-level DEBUG
```

## 10. Resources

- **Configuration Schema**: [schemas/ai-linter-config.schema.json](schemas/ai-linter-config.schema.json)
- **Configuration File**: [.ai-linter-config.yaml](.ai-linter-config.yaml)
- **Examples**: [examples/](examples/)

## 11. Quick Commands

```bash
# Basic validation
ai-linter .

# Validate skills only
ai-linter --skills .

# Custom config
ai-linter . --config-file my-config.yaml

# Debug mode
ai-linter . --log-level DEBUG

# Strict mode (fail on any warning)
ai-linter . --max-warnings 0

# Ignore specific dirs
ai-linter . --ignore node_modules build
```
