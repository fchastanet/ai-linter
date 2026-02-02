# Logging Format Implementation Summary

**Date:** 2026-02-01\
**Feature:** Multiple Logging Format Support (Factory & Adapter Pattern)

## Overview

Implemented a flexible logging format system allowing users to choose between three output formats: `logfmt` (existing),
`file-digest` (new, default), and `yaml` (new). The system uses the Factory and Adapter patterns for clean, extensible
architecture.

## Architectural Decisions

### Design Patterns Used

1. **Factory Pattern** (`LogFormatterFactory`): Creates formatter instances based on `LogFormat` enum
2. **Adapter Pattern** (Abstract `LogFormatter` base class): Adapts different formatting implementations to a common
   interface

### Key Components

#### 1. LogFormat Enum

```python
class LogFormat(Enum):
    LOGFMT = "logfmt"
    FILE_DIGEST = "file-digest"  # NEW - Default
    YAML = "yaml"               # NEW
```

#### 2. LogFormatter Hierarchy

- **Abstract Base**: `LogFormatter(ABC)` - Defines `format()` and `get_format()` methods
- **Implementations**:
  - `LogfmtFormatter`: Immediate printing (logfmt behavior preserved)
  - `FileDigestFormatter`: Groups errors by file with line numbers
  - `YamlFormatter`: Structured YAML output

#### 3. LogFormatterFactory

```python
@staticmethod
def create(format: LogFormat) -> LogFormatter:
    """Factory method to create appropriate formatter"""
```

#### 4. Logger Enhancements

- Added `_buffer_message()`: Stores messages during execution
- Added `flush()`: Outputs buffered messages using selected formatter
- Modified `log()`: Routes to appropriate formatter (immediate for logfmt, buffered for others)
- Added `set_format()`: Allows runtime format changes

### Configuration Support

#### Command-Line Argument

```bash
ai-linter --log-format file-digest .
ai-linter --log-format yaml .
ai-linter --log-format logfmt .
```

#### Configuration File (.ai-linter-config.yaml)

```yaml
log_format: yaml  # or "file-digest", "logfmt"
```

**Precedence**: CLI argument overrides config file setting

### Output Formats

#### LOGFMT (Existing Behavior - Preserved)

```
level="ERROR" rule="test-error" path="test.py" line="42" message="This is a test error"
```

- Immediate printing to stderr
- One line per error
- Log level format compatible with VS Code problem matchers

#### FILE-DIGEST (New - Default)

```
test.py
  (line 42):
    [line content would go here]
    ^-- test-error (ERROR): This is a test error

  (line 10):
    [line content would go here]
    ^-- test-warning (WARNING): This is a warning
```

- Groups errors by file
- Sorted by line number within each file
- Human-readable hierarchical format
- Placeholder for line content (extensible for future enhancement)

#### YAML (New)

```yaml
files:
  test.py:
    - level: ERROR
      rule: test-error
      message: This is a test error
      line: 42
    - level: WARNING
      rule: test-warning
      message: This is a warning
      line: 10
```

- Structured YAML format
- Suitable for machine processing
- Handles unknown files in `<unknown>` key

## Implementation Details

### Message Buffering Mechanism

**For LOGFMT format:**

- Messages printed immediately to stderr (preserves existing behavior)
- `flush()` call does nothing (returns empty string)

**For FILE-DIGEST and YAML formats:**

- Messages buffered in `Logger.messages` list during execution
- `flush()` called at program end (in `aiLinter.py:main()`)
- All messages formatted and output together

### Type Safety

- Used proper type annotations: `LogFormatter`, `LogFormat`
- Factory returns typed `dict[LogFormat, type[LogFormatter]]`
- All ABC methods properly abstract

### File Changes

1. **src/lib/log.py**:

   - Added `LogFormat` enum, `LogFormatter` ABC, three formatter implementations
   - Added `LogFormatterFactory`
   - Enhanced `Logger` class with buffering and format selection

2. **src/lib/config.py**:

   - Added `log_format` to `Config` class
   - Added config file loading for `log_format` setting
   - Updated `load_config()` signature and return type

3. **src/aiLinter.py**:

   - Added `--log-format` CLI argument
   - Initialize `Logger` with format from args/config
   - Call `logger.flush()` before program exit

## Testing & Quality

- ✅ All 32 existing tests pass
- ✅ No regression in functionality
- ✅ Code passes: black, isort, flake8, mypy, bandit
- ✅ Pre-commit hooks all pass
- ✅ Coverage maintained at 60%

## Future Enhancements

These were NOT implemented per requirements, but would be straightforward additions:

1. **Line Content Display**: Read actual file content to show in file-digest format
2. **Hint System**: Add structured hints/suggestions for each error
3. **Additional Formats**: e.g., JSON, HTML, Markdown
4. **Filtering**: Filter by rule, level, or file pattern before output

## Usage Examples

### Default behavior (file-digest)

```bash
ai-linter examples/
```

### Override with YAML format

```bash
ai-linter --log-format yaml examples/
```

### Config file with LOGFMT

```yaml
# .ai-linter-config.yaml
log_format: logfmt
log_level: INFO
```

### CLI overrides config

```bash
# Config says logfmt, but we want yaml:
ai-linter --log-format yaml examples/
```
