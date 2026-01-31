# Proposed Additional Linting Rules

This document contains ideas for future enhancements to the AI Linter based on best practices for AI-assisted
development.

## 1. High Priority Rules

### 1.1. Duplicate Content Detection

**Problem**: Same content repeated across multiple files wastes AI context

**Rule**: Detect when identical or highly similar content (>80% similarity) appears in multiple files

**Benefits**:

- Reduces redundancy
- Encourages DRY principles
- Identifies refactoring opportunities

**Configuration**:

```yaml
duplicate_detection:
  enabled: true
  similarity_threshold: 0.8  # 80% similarity
  ignore_patterns:
    - LICENSE
    - boilerplate.md
```

______________________________________________________________________

### 1.2. Broken Internal Link Detection

**Problem**: Links to non-existent sections or files break navigation

**Rule**: Validate all internal markdown links

**Checks**:

- File links: `[text](file.md)` - file exists
- Anchor links: `[text](#section)` - anchor exists in current file
- Combined: `[text](file.md#section)` - file and anchor both exist

**Configuration**:

```yaml
link_validation:
  check_anchors: true
  check_file_links: true
  level: ERROR
```

______________________________________________________________________

### 1.3. Skill Reference Validation

**Problem**: References to non-existent skills cause confusion

**Rule**: Validate that skill references point to actual SKILL.md files

**Detection**:

- `skill: skill-name` in AGENTS.md or prompts
- Check if `.github/skills/skill-name/SKILL.md` exists

**Configuration**:

```yaml
skill_validation:
  enabled: true
  skill_dirs:
    - .github/skills
  level: ERROR
```

______________________________________________________________________

### 1.4. Tool Availability Validation

**Problem**: Referencing unavailable tools leads to runtime errors

**Rule**: Verify that referenced tools are available

**Methods**:

- Check against known tool registry
- Validate against available VS Code commands
- Verify MCP server tools

**Configuration**:

```yaml
tool_validation:
  enabled: true
  tool_registry: .github/tools.yaml
  level: WARNING
```

______________________________________________________________________

### 1.5. YAML Schema Validation

**Problem**: Invalid frontmatter causes parsing errors

**Rule**: Validate frontmatter against JSON Schema

**Example Schema**:

```yaml
schema_validation:
  skill:
    required: [name, description]
    properties:
      name:
        type: string
        pattern: ^[a-z0-9-]+$
      description:
        type: string
        minLength: 10
        maxLength: 200
      version:
        type: string
        pattern: ^\d+\.\d+\.\d+$
```

______________________________________________________________________

## 2. Medium Priority Rules

### 2.1. Documentation Coverage Metrics

**Problem**: Unknown documentation completeness

**Rule**: Calculate what percentage of code files have corresponding documentation

**Metrics**:

- Files without documentation
- Functions/classes without docstrings
- Modules without README

**Output**:

```text
Documentation Coverage: 75%
- 15/20 Python files documented
- 50/80 functions have docstrings
- 3/5 modules have README
```

______________________________________________________________________

### 2.2. Prompt Template Validation

**Problem**: Inconsistent prompt structure across project

**Rule**: Validate prompts follow project-specific template

**Template Requirements**:

```markdown
# Required Sections
- ## Overview (required)
- ## Tools (required if any)
- ## Skills (required if any)
- ## Instructions (required)
- ## Examples (optional)
- ## References (optional)
```

**Configuration**:

```yaml
prompt_template:
  required_sections:
    - Overview
    - Instructions
  recommended_sections:
    - Examples
```

______________________________________________________________________

### 2.3. Version Consistency Validation

**Problem**: Version mismatches across skills and tools

**Rule**: Ensure version consistency

**Checks**:

- All skills using same version format
- Version in frontmatter matches git tags
- Dependencies specify compatible versions

**Configuration**:

```yaml
version_validation:
  format: semver    # semantic versioning
  check_git_tags: true
```

______________________________________________________________________

### 2.4. Language-Specific Linting

**Problem**: Generic linting misses language-specific issues

**Rule**: Apply language-specific rules to code snippets

**For Python**:

- Check for common anti-patterns
- Validate import statements
- Check for security issues (e.g., `eval()`, `exec()`)

**For JavaScript**:

- Check for `var` usage (prefer `const`/`let`)
- Validate async/await patterns

**Configuration**:

```yaml
language_linting:
  python:
    enabled: true
    rules:
      - no-eval
      - no-exec
      - prefer-pathlib
  javascript:
    enabled: true
    rules:
      - no-var
      - prefer-const
```

______________________________________________________________________

### 2.5. AI Context Size Optimization

**Problem**: Unknowingly approaching token limits

**Rule**: Calculate and report total AI context size

**Metrics**:

- Total tokens across all markdown files
- Warning when approaching typical context limits
- Suggestions for optimization

**Thresholds**:

```yaml
context_optimization:
  warn_threshold: 50000  # tokens
  error_threshold: 100000
  suggest_splitting: true
```

**Output**:

```text
⚠️  Total context size: 65,000 tokens
    Approaching limit (80,000 tokens)
    Consider:
    - Externalizing large code examples
    - Splitting large documents
    - Using more specific prompt files
```

______________________________________________________________________

## 3. Low Priority / Nice-to-Have

### 3.1. Markdown Style Consistency

**Problem**: Inconsistent markdown formatting

**Rule**: Enforce markdown style guide

**Checks**:

- Consistent heading levels (no skipping)
- Consistent list markers (-, \*, +)
- Consistent code fence markers (\` vs ~)
- Consistent emphasis (\*\* vs \_\_)

______________________________________________________________________

### 3.2. Image Optimization Validation

**Problem**: Large images bloat repository

**Rule**: Check image sizes and suggest optimization

**Checks**:

- Image file size > 1MB
- Non-web-optimized formats (BMP, TIFF)
- Suggest compression or format conversion

______________________________________________________________________

### 3.3. Accessibility Validation

**Problem**: Content not accessible to all users

**Rule**: Check for accessibility issues

**Checks**:

- Images have alt text
- Links have descriptive text (not "click here")
- Proper heading hierarchy
- Color contrast in examples

______________________________________________________________________

### 3.4. Security Pattern Detection

**Problem**: Security-sensitive patterns in documentation

**Rule**: Detect and warn about potential security issues

**Patterns to Detect**:

- Hardcoded API keys
- Passwords or tokens
- Private IP addresses
- Database connection strings

______________________________________________________________________

### 3.5. Performance Hints

**Problem**: Inefficient patterns in examples

**Rule**: Suggest performance improvements

**Examples**:

- Using `for` loops instead of list comprehensions
- Missing database indexes in examples
- N+1 query patterns
- Inefficient regex patterns

______________________________________________________________________

## 4. Implementation Considerations

### 4.1. For Each Rule

1. **Opt-in by default**: Allow users to enable gradually
2. **Configurable severity**: ERROR, WARNING, or INFO
3. **Clear error messages**: Explain what's wrong and how to fix
4. **Performance**: Don't slow down linting significantly
5. **False positive handling**: Provide escape hatches

### 4.2. Configuration Example

```yaml
# .ai-linter-config.yaml
advanced_rules:
  duplicate_detection: true
  broken_links: true
  skill_validation: true
  tool_validation: false  # Disabled for now
  schema_validation: true
  documentation_coverage: true
  prompt_template: true
  version_consistency: false
  language_linting: true
  context_optimization: true
  markdown_style: false
  image_optimization: false
  accessibility: true
  security_patterns: true
  performance_hints: false
```

______________________________________________________________________

## 5. Rule Priorities by Use Case

### 5.1. For Small Teams/Projects

1. Broken internal links
2. Skill reference validation
3. Code snippet size (already implemented ✅)
4. Unreferenced files (already implemented ✅)

### 5.2. For Large Organizations

1. Duplicate content detection
2. YAML schema validation
3. Version consistency
4. Tool availability validation
5. Documentation coverage

### 5.3. For AI-Heavy Workflows

1. AI context size optimization
2. Prompt template validation
3. Language-specific linting
4. Tool/skill validation

### 5.4. For Open Source Projects

1. Accessibility validation
2. Security pattern detection
3. Documentation coverage
4. Markdown style consistency

______________________________________________________________________

## 6. Implementation Roadmap

### 6.1. Phase 1 (Next Release)

- [ ] Broken internal link detection
- [ ] Skill reference validation
- [ ] Basic YAML schema validation

### 6.2. Phase 2 (Future)

- [ ] Tool availability validation
- [ ] Duplicate content detection
- [ ] Documentation coverage metrics

### 6.3. Phase 3 (Advanced)

- [ ] AI context size optimization
- [ ] Language-specific linting
- [ ] Security pattern detection

### 6.4. Phase 4 (Polish)

- [ ] Accessibility validation
- [ ] Markdown style consistency
- [ ] Performance hints

______________________________________________________________________

## 7. Community Input

These are proposals based on common pain points in AI-assisted development. Community feedback is welcome!

**How to provide feedback**:

1. Open an issue with `[rule-proposal]` tag
2. Describe your use case
3. Suggest priority level
4. Provide examples

**Vote on priorities**:

- 👍 = High priority, would use immediately
- 👀 = Interested, would try
- ❤️ = Would contribute implementation

______________________________________________________________________

## 8. Conclusion

The AI Linter can evolve into a comprehensive quality assurance tool for AI-assisted development. These proposed rules
would help teams:

- Maintain clean AI context
- Ensure documentation quality
- Catch issues early
- Follow best practices
- Optimize for AI effectiveness

Start with high-priority rules that solve immediate pain points, then gradually adopt others as the project matures.
