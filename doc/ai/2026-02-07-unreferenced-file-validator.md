# Unreferenced File Validator Implementation

**Date**: 2026-02-07 **Task**: Implement validation for unreferenced files in assets, references, and scripts
directories

## Original Problem Statement

The `validate_unreferenced_files` method should check that files in directories `assets`, `references`, and `scripts`
are referenced in:

- SKILL.md or md files referenced in SKILL.md
- AGENTS.md or md files referenced in AGENTS.md

This method should be called with the actual content of the SKILL.md or AGENTS.md where the file content has already
been retrieved.

## Implementation Summary

### 1. Created `UnreferencedFileValidator` Class

**Location**: `src/validators/unreferenced_file_validator.py`

**Key Features**:

- Validates that all files in `assets/`, `references/`, and `scripts/` directories are referenced in markdown content
- Extracts file references from:
  - Inline backtick references: `` `assets/file.txt` ``
  - Markdown links: `[text](path)`
  - Image references: `![alt](path)`
- Normalizes relative paths (handles `./` and `../`)
- Reports warnings for unreferenced files

**Main Method**:

```python
def validate_unreferenced_files(
    self, base_dir: Path, main_file: Path, content: str
) -> tuple[int, int]:
    """
    Validate that all files in assets/, references/, and scripts/ directories
    are referenced in the provided markdown content.

    Returns: (warning_count, error_count)
    """
```

### 2. Integration

The validator was integrated into:

**SkillValidator** (`src/validators/skill_validator.py`):

- Added `unreferenced_file_validator` parameter to `__init__`
- Calls `validate_unreferenced_files` after validating file references
- Passes skill directory, SKILL.md path, and skill content

**AgentValidator** (`src/validators/agent_validator.py`):

- Added `unreferenced_file_validator` parameter to `__init__`
- Calls `validate_unreferenced_files` after validating content length
- Passes agent file parent directory, AGENTS.md path, and agent content

**Main Entry Point** (`src/aiLinter.py`):

- Instantiates `UnreferencedFileValidator`
- Passes it to both `SkillValidator` and `AgentValidator`

### 3. Testing

Created comprehensive test suite in `src/validators/unreferenced_file_validator_test.py`:

- Test with no directories
- Test when all files are referenced
- Test with unreferenced files
- Test markdown link references
- Test relative path normalization
- Test nested directories
- Test file reference extraction
- Test path normalization

All tests pass successfully (9/9).

## Validation Rules

### Checked Directories

- `assets/` - Asset files (images, documents, etc.)
- `references/` - Reference documentation
- `scripts/` - Script files

### Reference Detection

The validator extracts file references from:

1. **Inline code blocks**: `` `path/to/file` ``
2. **Markdown links**: `[Link Text](path/to/file)`
3. **Image references**: `![Alt Text](path/to/file.png)`

### Path Normalization

- Removes leading `./`
- Resolves `../` relative paths
- Handles both forward and backward slashes
- Compares normalized paths for matching

### Reporting

- **Level**: WARNING (not ERROR)
- **Code**: `unreferenced-file`
- **Message**: "File '{relative_path}' is not referenced in {file_name}"

## Usage Example

Given a skill structure:

```
my-skill/
  SKILL.md
  assets/
    logo.png
    icon.png
  references/
    guide.md
  scripts/
    helper.py
```

If `SKILL.md` contains:

```markdown
# My Skill

See `assets/logo.png` and [Guide](references/guide.md)
```

The validator will report warnings for:

- `assets/icon.png` (not referenced)
- `scripts/helper.py` (not referenced)

## Documentation Updates

Updated `AGENTS.md`:

- Added `unreferenced_file_validator.py` to validators list
- Added unreferenced file checking to Skills Validation checks
- Added unreferenced file checking to Agents Validation checks
- Added `unreferenced-file` to error codes list

## Testing Results

### Unit Tests

```
Ran 9 tests in 0.006s
OK
```

### Integration Test

Created test with:

- Referenced files: `assets/logo.png`, `references/guide.md`
- Unreferenced files: `assets/icon.png`, `scripts/helper.py`

Result: ✅ 2 warnings as expected, 0 errors

## Benefits

1. **Prevents Dead Files**: Identifies files that are in the repository but not actually used
2. **Maintains Cleanliness**: Helps keep skill directories clean and organized
3. **Documentation**: Ensures all asset files are documented in the markdown files
4. **Non-Breaking**: Uses warnings rather than errors, allowing validation to continue

## Future Enhancements

Potential improvements for future consideration:

1. Support for checking referenced markdown files recursively
2. Option to ignore certain files/patterns
3. Configurable severity (warning vs error)
4. Support for wildcard patterns in references
5. Check for broken internal links between markdown files

## Implementation Notes

- The validator accepts the actual content string, not file paths, as specified in requirements
- File content has already been retrieved by the calling validator (SkillValidator or AgentValidator)
- The implementation is minimal and focused, making only necessary changes
- Integration follows existing patterns in the codebase
- Tests follow the existing unittest pattern used in the project
