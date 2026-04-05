---
name: test-ignore-errors
description: Test skill demonstrating file link error exclusion patterns for false positives.
license: MIT
compatibility: Test skill for demonstrating ignore patterns
metadata:
  author: test-author
  version: "1.0"
---

# Test Ignore Errors Skill

This skill demonstrates various file link patterns that should be excluded from validation.

## Architecture

This skill supports multiple architectures:

- `linux/amd64` - x86-64 architecture
- `linux/arm64` - ARM 64-bit architecture
- `linux/arm/v7` - ARM 32-bit architecture v7

See [Docker Build Options](references/build-options.md) for details.

## Memory Management

The skill uses session memory for analysis:

- Analysis phase 1: `/memories/session/mongodb-analysis-phase1.json`
- Analysis phase 2: `/memories/session/mongodb-analysis-phase2.json`
- Generic phase: `/memories/session/mongodb-analysis-{phase}.json`

## Shell Scripts

Example shell script headers:

- `#!/bin/bash` - Bash script
- `#!/usr/bin/env python3` - Python script
- `#!/bin/sh` - Shell script

## Template References

Documentation templates with placeholders:

- `docs/ai/{date}/analysis.md` - Date-based documentation
- `docs/reports/{quarter}-report.md` - Quarterly reports

## Valid References

These files should actually exist:

- [Build Options](references/build-options.md)
- [Configuration Guide](references/config.md)

## Not Found References (These are intentional for testing)

- [Missing File](nonexistent/missing-file.md)
