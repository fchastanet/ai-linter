# AI Linter - Quick Reference Guide

## 1. New Enhanced Features

### 1.1. Code Snippet Validation 📦

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

______________________________________________________________________

### 1.2. Unreferenced File Detection 🔗

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

______________________________________________________________________

### 1.3. Prompt/Agent Validation 🤖

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

______________________________________________________________________

### 1.4. AGENTS.md Requirement 📄

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

______________________________________________________________________

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

______________________________________________________________________

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

______________________________________________________________________

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

______________________________________________________________________

### 3.3. Maintain Prompt Quality

**Problem**: Prompts getting too long and unfocused

**Solution**: Use prompt/agent validation

**Fix**:

- Split large prompts into:
  - Main prompt (core instructions)
  - Reference documents
  - Separate skills
- Keep each under 5000 tokens

______________________________________________________________________

### 3.4. Improve AI Assistant Onboarding

**Problem**: AI assistants don't understand project structure

**Solution**: Create AGENTS.md

**Template**:

```markdown
# Project Name

## 4. Overview
[Brief description]

## 5. Structure
[Directory layout with descriptions]

## 6. Key Components
[Important files/modules]

## 7. Guidelines
[Coding standards, patterns]

## 8. Common Tasks
[How to add features, run tests, etc.]
```

______________________________________________________________________

## 9. Error Codes Reference

| Code                          | Level              | Description                     |
| ----------------------------- | ------------------ | ------------------------------- |
| `code-snippet-too-large`      | WARNING            | Code block exceeds max lines    |
| `unreferenced-resource-file`  | ERROR/WARNING/INFO | File not referenced in markdown |
| `prompt-content-too-long`     | WARNING            | Prompt exceeds 500 lines        |
| `prompt-token-count-exceeded` | WARNING            | Prompt exceeds 5000 tokens      |
| `agents-file-missing`         | WARNING/ERROR/INFO | AGENTS.md not found             |
| `tools-found`                 | INFO               | Tool references detected        |
| `skills-found`                | INFO               | Skill references detected       |

______________________________________________________________________

## 10. Best Practices

### 10.1. ✅ DO

- Keep code snippets minimal (≤3 lines)
- Reference all resource files in documentation
- Split large prompts into modular pieces
- Create and maintain AGENTS.md
- Use configuration file for project standards
- Run linter in pre-commit hooks

### 10.2. ❌ DON'T

- Embed large code blocks in markdown
- Accumulate unused resource files
- Create 1000+ line prompt files
- Skip AGENTS.md for non-trivial projects
- Ignore linter warnings without review

______________________________________________________________________

## 11. Configuration Presets

### 11.1. Strict Mode (High Quality)

```yaml
log_level: INFO
max_warnings: 0
code_snippet_max_lines: 3
unreferenced_file_level: ERROR
missing_agents_file_level: ERROR
```

### 11.2. Balanced Mode (Recommended)

```yaml
log_level: INFO
max_warnings: 10
code_snippet_max_lines: 5
unreferenced_file_level: ERROR
missing_agents_file_level: WARNING
```

### 11.3. Lenient Mode (Large Projects)

```yaml
log_level: WARNING
max_warnings: 50
code_snippet_max_lines: 10
unreferenced_file_level: WARNING
missing_agents_file_level: INFO
```

______________________________________________________________________

## 12. Troubleshooting

### 12.1. Too Many Warnings

**Problem**: Linter fails with too many warnings

**Solution**:

1. Increase `max_warnings` temporarily
2. Fix issues incrementally
3. Lower back to desired threshold

### 12.2. False Positives

**Problem**: File flagged as unreferenced but it is referenced

**Solution**:

1. Check reference format (relative paths)
2. Ensure reference in markdown link: `[text](path)`
3. Verify file path is correct

### 12.3. Configuration Not Loading

**Problem**: Changes to config file not reflected

**Solution**:

1. Verify file is `.ai-linter-config.yaml`
2. Check file is in project root or specified with `--config-file`
3. Validate YAML syntax

______________________________________________________________________

## 13. Integration Examples

### 13.1. Pre-commit Hook

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

### 13.2. GitHub Actions

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

### 13.3. Makefile

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

______________________________________________________________________

## 14. Resources

- **Full Documentation**: [Enhanced Linting Rules](docs/ENHANCED_LINTING_RULES.md)
- **Implementation Details**: [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
- **Configuration**: [.ai-linter-config.yaml](.ai-linter-config.yaml)
- **Examples**: [examples/](examples/)

______________________________________________________________________

## 15. Quick Commands

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
ai-linter . --ignore-dirs node_modules build
```

______________________________________________________________________

**Need Help?** Check the [full documentation](docs/ENHANCED_LINTING_RULES.md) or open an issue!
