# Agents Configuration

This file contains agent configurations for the AI Linter project.

## Development Agent

This agent assists with development tasks:

- Code validation and linting
- Documentation generation
- Test execution
- Build automation

**Capabilities:**

- File system access for reading source files
- Execution of validation scripts
- Generation of reports
- Integration with development tools

## Validation Agent

This agent focuses on content validation:

- Skill file validation
- Frontmatter parsing
- Token counting
- Reference checking

**Files processed:**

- [SKILL.md](../sample-skill/SKILL.md) files in skill directories
- Configuration files
- Documentation files

**Validation rules:**

- Content length limits
- Token count restrictions
- Required frontmatter properties
- File reference integrity

## Usage Notes

These agents are configured to work with the AI Linter tool and follow the validation rules
defined in the codebase. They process files according to the specified criteria and generate
detailed reports on validation status.
