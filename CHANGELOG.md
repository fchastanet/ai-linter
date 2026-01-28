# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1. [Unreleased]

### 1.1. Added

- Initial release of AI Linter
- Validation for AI skills (`SKILL.md` files)
- Validation for AI agents (`AGENTS.md` files)
- Frontmatter validation with YAML parsing
- File reference validation
- Token counting using tiktoken
- Configurable validation rules
- Pre-commit hooks integration
- Comprehensive documentation

### 1.2. Features

- Support for multiple directories validation
- Auto-discovery of skills with `--skills` flag
- Configurable warning limits
- Directory ignore patterns
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- YAML configuration file support
- Detailed error reporting with file locations

### 1.3. Developer Tools

- Pre-commit configuration with multiple linters
- GitHub Actions CI/CD pipeline
- Makefile for common development tasks
- Modern Python packaging with pyproject.toml
- Test structure with pytest
- Code formatting with Black and isort
- Linting with flake8 and mypy

## 2. [0.1.0] - 2026-01-26

### 2.1. Added

- Initial version inspired by Anthropic's skill validation script
- Basic skill and agent validation functionality
- Core library structure with modular design
