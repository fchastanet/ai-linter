# Release Guide for AI Linter

<!--TOC-->

- [1. Prerequisites](#1-prerequisites)
- [2. Pre-Release Checklist](#2-pre-release-checklist)
  - [2.1. Version Verification](#21-version-verification)
  - [2.2. Documentation Updates](#22-documentation-updates)
  - [2.3. Quality Checks](#23-quality-checks)
  - [2.4. Clean Working Directory](#24-clean-working-directory)
- [3. Release Process](#3-release-process)
  - [3.1. Step 1: Create Release Branch (Optional)](#31-step-1-create-release-branch-optional)
  - [3.2. Step 2: Update Version Numbers](#32-step-2-update-version-numbers)
  - [3.3. Step 3: Update CHANGELOG.md](#33-step-3-update-changelogmd)
  - [4.5. Step 4: Commit Changes](#45-step-4-commit-changes)
  - [4.6. Step 5: Create Git Tag](#46-step-5-create-git-tag)
  - [4.7. Step 6: Create GitHub Release](#47-step-6-create-github-release)
  - [4.8. Step 7: Automated PyPI Upload](#48-step-7-automated-pypi-upload)
- [5. Manual PyPI Upload (if needed)](#5-manual-pypi-upload-if-needed)
- [6. Post-Release Tasks](#6-post-release-tasks)
  - [6.1. Verify Release](#61-verify-release)
  - [6.2. Update Documentation](#62-update-documentation)
  - [6.3. Prepare for Next Version](#63-prepare-for-next-version)
- [7. Version Numbering](#7-version-numbering)
- [8. Release Types](#8-release-types)
  - [8.1. Patch Release (0.1.1)](#81-patch-release-011)
  - [8.2. Minor Release (0.2.0)](#82-minor-release-020)
  - [8.3. Major Release (1.0.0)](#83-major-release-100)
- [9. Troubleshooting](#9-troubleshooting)
  - [9.1. PyPI Upload Fails](#91-pypi-upload-fails)
  - [9.2. GitHub Actions Fails](#92-github-actions-fails)
  - [9.3. Version Mismatch](#93-version-mismatch)
- [10. Rollback Process](#10-rollback-process)
- [11. Security Releases](#11-security-releases)
- [12. Support](#12-support)

<!--TOC-->

This document provides step-by-step instructions for creating a new release of AI Linter.

## 1. Prerequisites

Before creating a release, ensure you have:

1. **Push access** to the repository
2. **PyPI account** with upload permissions
3. **Local development environment** properly set up
4. **All changes merged** into the main branch
5. **Tests passing** in CI/CD

## 2. Pre-Release Checklist

### 2.1. Version Verification

Check that the version is correctly set in:

- [ ] `pyproject.toml` - `[project]` section `version` field
- [ ] `src/ai_linter.py` - `AI_LINTER_VERSION` constant

### 2.2. Documentation Updates

- [ ] Update [CHANGELOG.md](CHANGELOG.md) with new version and changes
- [ ] Review [README.md](README.md) for accuracy
- [ ] Update any version references in documentation

### 2.3. Quality Checks

Run the full test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all checks
make check-all

# Test the package locally
make validate
```

### 2.4. Clean Working Directory

Ensure your working directory is clean:

```bash
git status
# Should show "working tree clean"
```

## 3. Release Process

### 3.1. Step 1: Create Release Branch (Optional)

For major releases, consider creating a release branch:

```bash
git checkout -b release/v0.2.0
```

### 3.2. Step 2: Update Version Numbers

Update the version in both files:

```bash
# In pyproject.toml
version = "0.2.0"

# In src/ai_linter.py
AI_LINTER_VERSION = "0.2.0"
```

### 3.3. Step 3: Update CHANGELOG.md

Add a new section for the release:

```markdown
## 4. [0.2.0] - 2026-01-27

### 4.1. Added
- New feature descriptions

### 4.2. Changed
- Modified functionality descriptions

### 4.3. Fixed
- Bug fixes

### 4.4. Removed
- Deprecated feature removals
```

### 4.5. Step 4: Commit Changes

```bash
git add pyproject.toml src/ai_linter.py CHANGELOG.md
git commit -m "chore: bump version to v0.2.0"
git push origin main
```

### 4.6. Step 5: Create Git Tag

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

### 4.7. Step 6: Create GitHub Release

1. Go to the [GitHub repository](https://github.com/fchastanet/ai-linter)
2. Click "Releases" → "Create a new release"
3. Select the tag you just created (`v0.2.0`)
4. Set release title: `AI Linter v0.2.0`
5. Add release notes (copy from CHANGELOG.md)
6. Check "Set as the latest release" if applicable
7. Click "Publish release"

### 4.8. Step 7: Automated PyPI Upload

The GitHub Actions workflow should automatically:

1. Build the package
2. Upload to PyPI

Monitor the [Actions tab](https://github.com/fchastanet/ai-linter/actions) to ensure success.

## 5. Manual PyPI Upload (if needed)

If automated upload fails:

```bash
# Clean previous builds
make clean

# Build the package
make build

# Upload to PyPI
make upload
```

Or manually:

```bash
# Install build tools
pip install build twine

# Build
python -m build

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## 6. Post-Release Tasks

### 6.1. Verify Release

- [ ] Check [PyPI](https://pypi.org/project/ai-linter/) for the new version
- [ ] Test installation: `pip install ai-linter==0.2.0`
- [ ] Verify the command works: `ai-linter --version`

### 6.2. Update Documentation

- [ ] Update any deployment or installation guides
- [ ] Notify users on relevant channels
- [ ] Update project README if needed

### 6.3. Prepare for Next Version

Optionally bump to the next development version:

```bash
# In pyproject.toml and src/ai_linter.py
version = "0.3.0-dev"
AI_LINTER_VERSION = "0.3.0-dev"

git add .
git commit -m "chore: bump to next development version"
git push origin main
```

## 7. Version Numbering

AI Linter follows [Semantic Versioning](https://semver.org/):

- **Major (X.0.0)**: Breaking changes, incompatible API changes
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, backward compatible

## 8. Release Types

### 8.1. Patch Release (0.1.1)

- Bug fixes
- Minor documentation updates
- No new features

### 8.2. Minor Release (0.2.0)

- New features
- Enhanced functionality
- Backward compatible changes

### 8.3. Major Release (1.0.0)

- Breaking changes
- Major architectural changes
- API changes that break backward compatibility

## 9. Troubleshooting

### 9.1. PyPI Upload Fails

1. **Authentication Error**: Ensure `PYPI_API_TOKEN` secret is set correctly
2. **Version Conflict**: Version already exists on PyPI - bump version number
3. **Package Validation**: Run `twine check dist/*` to validate package

### 9.2. GitHub Actions Fails

1. Check the Actions tab for detailed error logs
2. Ensure all required secrets are configured
3. Verify the workflow file syntax

### 9.3. Version Mismatch

If versions get out of sync:

1. Manually update both files to match
2. Create a new commit with correct versions
3. Re-tag if necessary: `git tag -d v0.2.0 && git push origin :v0.2.0`

## 10. Rollback Process

If a release needs to be rolled back:

1. **Remove from PyPI**: Contact PyPI support (versions cannot be re-uploaded)
2. **Mark GitHub release as pre-release**: Edit the release on GitHub
3. **Revert changes**: Create a new release with fixes
4. **Communicate**: Notify users of the issue and resolution

## 11. Security Releases

For security-related releases:

1. **Private coordination**: Coordinate with security team if applicable
2. **CVE assignment**: Request CVE if needed
3. **Security advisory**: Create GitHub security advisory
4. **Expedited process**: Skip some testing for critical fixes
5. **Clear communication**: Mark release notes with security information

## 12. Support

For questions about the release process:

- Create an issue on GitHub
- Contact maintainers directly
- Check the [CONTRIBUTING.md](CONTRIBUTING.md) guide

Remember to keep this document updated as the release process evolves!
