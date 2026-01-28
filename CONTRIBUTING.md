# Contributing to AI Linter

We welcome contributions to the AI Linter project! This document provides guidelines for contributing.

## 1. Development Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd ai-linter
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**

   ```bash
   make install-dev
   # or manually:
   pip install -e ".[dev]"
   pre-commit install
   ```

## 2. Development Workflow

### 2.1. Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all formatting and checks:

```bash
make check-all
```

### 2.2. Pre-commit Hooks

Pre-commit hooks are configured to run automatically before each commit:

```bash
# Install hooks
make pre-commit

# Run manually
pre-commit run --all-files
```

### 2.3. Testing

Run tests with:

```bash
make test
# or
pytest
```

### 2.4. Validation

Test the linter itself:

```bash
# Basic validation
make validate

# Debug mode
make validate-debug
```

## 3. Submitting Changes

### 3.1. Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the coding standards
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Run all checks** with `make check-all`
6. **Submit a pull request** with a clear description

### 3.2. Commit Messages

Use clear, descriptive commit messages:

```text
feat: add new validation rule for agent metadata
fix: resolve token counting issue with special characters
docs: update installation instructions
test: add unit tests for skill validator
```

### 3.3. Branch Naming

Use descriptive branch names:

```text
feature/add-metadata-validation
fix/token-count-bug
docs/improve-readme
refactor/validator-structure
```

## 4. Adding New Features

### 4.1. New Validators

1. Create validator in `src/validators/`
2. Follow existing patterns (inherit from base if needed)
3. Add comprehensive error handling
4. Include detailed logging
5. Add tests

### 4.2. New Configuration Options

1. Update `load_config()` in `src/lib/config.py`
2. Add to example config file
3. Update documentation
4. Add validation for the new option

### 4.3. New Command Line Arguments

1. Add to argument parser in `src/aiLinter.py`
2. Update help text
3. Document in README.md
4. Consider adding to configuration file options

## 5. Code Guidelines

### 5.1. Python Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

### 5.2. Error Handling

- Use structured logging with error codes
- Provide helpful error messages
- Include file paths and line numbers when relevant
- Distinguish between warnings and errors

### 5.3. Testing

- Write unit tests for new functionality
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests isolated and independent

## 6. Project Structure

```text
ai-linter/
├── src/
│   ├── aiLinter.py          # Main entry point
│   ├── lib/                 # Core utilities
│   ├── processors/          # Data processors
│   └── validators/          # Validation logic
├── tests/                   # Test suite
├── .github/                 # GitHub Actions
└── docs/                    # Documentation
```

## 7. Getting Help

- Open an issue for bugs or feature requests
- Use discussions for questions and ideas
- Check existing issues before creating new ones
- Provide detailed information and examples

## 8. Code of Conduct

- Be respectful and inclusive
- Focus on the technical aspects
- Help newcomers learn and contribute
- Maintain a professional tone

Thank you for contributing to AI Linter!
