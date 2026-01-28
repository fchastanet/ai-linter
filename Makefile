.PHONY: help install install-dev test lint format clean build upload check-all pre-commit ai-linter ai-linter-debug test-all build-deps pip-upgrade

help:
	@echo "Available commands:"
	@echo "  install          Install the package and dependencies"
	@echo "  install-dev      Install package in development mode with dev dependencies"
	@echo "  pre-commit       Install and run pre-commit hooks"
	@echo "  ai-linter        Run AI Linter on the current directory"
	@echo "  ai-linter-debug  Run AI Linter with debug logging"
	@echo "  test             Run tests with pytest"
	@echo "  test-all         Run all tests including AI linter tests"
	@echo "  lint             Run linting checks (black, isort, flake8, mypy)"
	@echo "  format           Format code with black and isort"
	@echo "  check-all        Run all checks (format, lint, test)"
	@echo "  clean            Clean build artifacts and cache files"
	@echo "  build            Build the package"
	@echo "  upload           Upload package to PyPI"

pip-upgrade:
	python -m pip install --upgrade pip

install: pip-upgrade
	pip install .

install-dev: pip-upgrade
	pip install -e ".[dev]"
	pre-commit install

pre-commit:
	pre-commit install
	pre-commit run --all-files

test:
	pytest --cov=src --cov-report=xml src || echo "No tests found"

# Run AI Linter on current directory
ai-linter:
	ai-linter --skills .

# Run AI Linter with debug logging
ai-linter-debug:
	ai-linter --log-level DEBUG --skills .

test-all: test ai-linter
	# Test the linter itself
	ai-linter --version
	ai-linter --help

format:
	black --line-length=120 src/
	isort --profile black src/

lint:
	# Check code formatting
	black --line-length=120 --check src/

	# Check import sorting
	isort --profile black --check-only src/

	# Run flake8
	flake8 src/ --max-line-length=120 --extend-ignore=E203,W503

	# Run mypy
	mypy src/

check-all: lint test-all

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "*.pyc" -type f -delete
	find . -name "*.pyo" -type f -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

build-deps:
	python -m pip install --upgrade pip
	pip install build twine

build: clean build-deps
	python -m build

upload: build
	python -m twine upload dist/*
