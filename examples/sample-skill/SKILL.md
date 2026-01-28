---
name: sample-ai-skill
description: A sample skill demonstrating the AI Linter validation
license: MIT
allowed-tools:
  - text-editor
  - file-system
metadata:
  author: AI Linter Example
  version: "1.0.0"
  tags: ["example", "validation", "demo"]
compatibility:
  frameworks: ["anthropic", "openai"]
  languages: ["python", "javascript"]
---

# Sample AI Skill

This is an example skill file that demonstrates the proper format for AI skills that will pass AI Linter validation.

## Purpose

This skill serves as an example of:

- Proper frontmatter formatting
- Correct metadata structure
- Valid file references
- Appropriate content length

## Implementation

The skill implementation would go here. This content is validated for:

- Token count (must be under 5000 tokens)
- Line count (must be under 500 lines)
- File references (all must exist)

## Files

This skill references the following files:

- [README.md](../../README.md) - Main documentation
- [pyproject.toml](../../pyproject.toml) - Package configuration

## Usage

Example usage instructions would be provided here.
