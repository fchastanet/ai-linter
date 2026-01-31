# Enhanced Linting Rules for AI-Assisted Development

This document describes the enhanced linting rules for AGENTS.md, SKILLS.md, and prompt files to improve AI assistant
effectiveness and maintain clean, maintainable AI context.

## 1. Overview

The AI Linter now includes advanced validation rules designed to:

1. **Minimize AI context size** by detecting oversized code snippets
2. **Ensure resource integrity** by validating file references
3. **Maintain prompt quality** through token count and structure validation
4. **Improve discoverability** by requiring AGENTS.md documentation

## 2. New Linting Rules

### 2.1. Code Snippet Size Validation

**Purpose**: Prevent bloated AI context by encouraging externalization of large code blocks.

**Rule**: Code blocks in markdown files should not exceed a configurable line limit (default: 3 lines).

**Rationale**:

- Large code snippets increase token consumption
- External files can be loaded on-demand by AI assistants
- Better separation of concerns and maintainability

**Configuration**:

```yaml
# .ai-linter-config.yaml
code_snippet_max_lines: 3  # Adjust based on your needs
```

**Examples**:

✅ **Good** - Small, illustrative snippet:

````markdown
Use the following pattern:
```python
result = process_data(input)
```
````

❌ **Bad** - Large implementation that should be external:

````markdown
Here's the complete implementation:
```python
def complex_function(data):
    # 50+ lines of implementation
    # This should be in a separate file!
    ...
```
````

**Fix**: Move large code blocks to external files:

```markdown
See the implementation in [process.py](scripts/process.py)
```

______________________________________________________________________

### 2.2. Unreferenced Resource File Detection

**Purpose**: Ensure all resource files are actually used and referenced in documentation.

**Rule**: All files in `references/`, `assets/`, and `scripts/` directories must be referenced in at least one markdown
file.

**Rationale**:

- Prevents accumulation of unused files
- Ensures documentation stays synchronized with resources
- Helps identify dead code and outdated resources

**Configuration**:

```yaml
# .ai-linter-config.yaml
resource_dirs:
  - references
  - assets
  - scripts
unreferenced_file_level: ERROR  # or WARNING, INFO
```

**Detection Methods**: The linter looks for references in:

- Markdown links: `[text](path/to/file)`
- Images: `![alt](path/to/image.png)`
- HTML tags: `<img src="path">`
- Attachments: `<attachment filePath="path">`
- Code comments: `source: path/to/file`

**Examples**:

✅ **Good** - Referenced file:

```markdown
# Documentation

See the utility script in [scripts/helper.sh](scripts/helper.sh)
```

❌ **Bad** - File exists but not referenced:

```text
scripts/
  └── unused_script.sh  # No markdown file references this!
```

**Fix**: Either:

1. Add a reference in appropriate markdown documentation
2. Remove the unused file
3. Move it to a non-resource directory if it's for internal use only

______________________________________________________________________

### 2.3. Prompt and Agent Directory Validation

**Purpose**: Ensure consistency and quality of AI prompts and agent configurations.

**Rules**:

1. **Token Count**: Files should not exceed 5000 tokens (approximate)
2. **Line Count**: Files should not exceed 500 lines
3. **File References**: All referenced files must exist
4. **Tool References**: Extracted and logged for documentation
5. **Skill References**: Extracted and logged for validation

**Configuration**:

```yaml
# .ai-linter-config.yaml
prompt_dirs:
  - .github/prompts

agent_dirs:
  - .github/agents
```

**What Gets Validated**:

**For `.github/prompts/` files**:

- Content size (lines and tokens)
- File references are valid
- Tool and skill references are extracted

**For `.github/agents/` files**:

- Same as prompts
- Tool usage patterns
- Skill dependencies

**Examples**:

✅ **Good** - Well-structured prompt:

```markdown
# Code Review Agent

## 3. Tools
tool: grep_search
tool: read_file

## 4. Skills
skill: python-linting
skill: code-quality

## 5. Instructions
Review code for quality issues using the provided tools.

[Reference Guide](references/review-checklist.md)
```

❌ **Bad** - Oversized, unfocused prompt:

```markdown
# Giant Prompt

[700 lines of instructions and examples]
[Token count: 8000+]
```

**Fix**: Split large prompts into:

1. Main prompt file (core instructions)
2. Reference documents (detailed examples)
3. Separate skill files (reusable behaviors)

______________________________________________________________________

### 5.1. Missing AGENTS.md Detection

**Purpose**: Ensure projects provide AI assistant guidance.

**Rule**: Projects should have an `AGENTS.md` file in the root directory.

**Rationale**:

- AGENTS.md provides AI assistants with project context
- Improves AI effectiveness and accuracy
- Documents coding standards and patterns
- Reduces repetitive explanations

**Configuration**:

```yaml
# .ai-linter-config.yaml
missing_agents_file_level: WARNING  # or ERROR, INFO
```

**What Should Be in AGENTS.md**:

````markdown
# Project Name

## 6. Project Overview
Brief description of the project, its purpose, and architecture.

## 7. Project Structure

```text
src/
  ├── components/  # React components
  ├── utils/       # Utility functions
  └── types/       # TypeScript definitions
````

## 8. Key Components

- **ComponentName**: Description and usage
- **UtilityFunction**: Purpose and parameters

## 9. Development Guidelines

- Code style requirements
- Testing approach
- Common patterns

## 10. Extension Points

How to add new features or extend existing ones.

## 11. Working with AI Agents

- Recommended tools for this project
- Available skills
- Testing procedures

______________________________________________________________________

## 12. Best Practices

### 12.1. For Code Snippets

1. **Keep snippets minimal**: Show only the relevant parts
2. **Use ellipsis for omissions**: `// ... rest of implementation`
3. **Link to full implementations**: Use markdown links to actual files
4. **Prefer external files**: For anything over 3 lines

### 12.2. For Resource Files

1. **Document everything**: Every file should have a purpose
2. **Link from relevant docs**: Reference files where they're used
3. **Use consistent paths**: Relative paths from project root
4. **Clean up regularly**: Remove unused resources

### 12.3. For Prompts and Agents

1. **Be concise**: Stay under token limits
2. **Reference don't duplicate**: Link to docs instead of copying
3. **Organize hierarchically**: Main prompt → skills → references
4. **Document dependencies**: List required tools and skills

### 12.4. For AGENTS.md

1. **Keep it updated**: Sync with code changes
2. **Be specific**: Concrete examples over abstract descriptions
3. **Include context**: Architecture, patterns, conventions
4. **Guide AI effectively**: Clear instructions for common tasks

______________________________________________________________________

## 13. Configuration Reference

Complete `.ai-linter-config.yaml` example:

```yaml
# Logging
log_level: INFO
max_warnings: 10

# Directories to ignore
ignore_dirs:
  - .git
  - __pycache__
  - node_modules
  - build
  - dist
  - .vscode
  - .pytest_cache
  - venv
  - env

# Code snippet validation
code_snippet_max_lines: 3

# Prompt/agent directories
prompt_dirs:
  - .github/prompts
agent_dirs:
  - .github/agents

# Resource directories
resource_dirs:
  - references
  - assets
  - scripts

# Severity levels
unreferenced_file_level: ERROR
missing_agents_file_level: WARNING
```

______________________________________________________________________

## 14. Error Codes

### 14.1. Code Snippet Errors

- **`code-snippet-too-large`**: Code block exceeds maximum line count

### 14.2. Unreferenced File Errors

- **`unreferenced-resource-file`**: File in resource directory not referenced in any markdown

### 14.3. Prompt/Agent Errors

- **`prompt-content-too-long`**: File exceeds maximum line count
- **`prompt-token-count-exceeded`**: File exceeds maximum token count
- **`agents-file-missing`**: AGENTS.md not found in root directory

______________________________________________________________________

## 15. Migration Guide

### 15.1. Existing Projects

1. **Run initial scan**:

   ```bash
   ai-linter --skills .
   ```

2. **Address code snippets**:

   - Identify large code blocks
   - Extract to files in `scripts/` or `references/`
   - Update markdown to reference external files

3. **Clean up resources**:

   - Review unreferenced files
   - Add references or remove unused files

4. **Create AGENTS.md**:

   - Use template above
   - Document project structure
   - Add development guidelines

5. **Validate prompts**:

   - Check token counts
   - Split oversized files
   - Validate file references

### 15.2. New Projects

1. **Start with AGENTS.md**: Create from template
2. **Configure linter**: Add `.ai-linter-config.yaml`
3. **Organize resources**: Use standard directory structure
4. **Keep snippets small**: Follow 3-line guideline from start
5. **Document continuously**: Update as you develop

______________________________________________________________________

## 16. FAQ

**Q: Why limit code snippets to 3 lines?** A: This is configurable. The goal is to keep markdown focused on
documentation while encouraging proper code organization in external files. Adjust based on your needs.

**Q: What if I have many small, rarely-used resource files?** A: Create an index document that lists all resources with
their purposes. This satisfies the reference requirement and improves discoverability.

**Q: Can I disable specific validators?** A: Yes, set severity to `INFO` in config, or use `--ignore-dirs` to skip
directories. Consider why you want to disable them though - the rules exist to improve code quality.

**Q: How are tokens counted?** A: Currently a simple whitespace split approximation. Actual AI tokenization may differ
slightly. The limit provides a reasonable guideline.

**Q: Do I need AGENTS.md if my project is tiny?** A: Even small projects benefit from basic documentation. A minimal
AGENTS.md can be just a few lines explaining the project's purpose.

______________________________________________________________________

## 17. Additional Resources

- [AGENTS.md Template](https://github.com/user/ai-linter/blob/main/examples/AGENTS.md)
- [Best Practices Guide](https://www.builder.io/blog/agents-md)
- [AI Context Optimization](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)

______________________________________________________________________

## 18. Contributing

Found a useful linting rule we should add? Please open an issue or PR!

**Suggested future rules**:

- Detect duplicate content across files
- Validate YAML frontmatter schemas
- Check for broken internal links
- Measure documentation coverage
- Validate skill references against actual skill files
