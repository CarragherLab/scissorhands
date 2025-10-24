# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-27

### Added
- Modern Python packaging with `pyproject.toml`
- Source layout (`src/` directory structure)
- Development dependencies (pytest, ruff, mypy, build)
- Python 3.9+ support
- Comprehensive tool configuration
- CHANGELOG.md for version tracking

### Changed
- Migrated from `setup.py` to `pyproject.toml`
- Updated package structure to modern src layout
- Enhanced `.gitignore` with modern Python patterns
- Updated README.md with modern installation instructions
- Removed Travis CI badge (outdated)

### Technical Details
- Build system: hatchling (modern, pure Python)
- No runtime dependencies (remains lightweight)
- Development tools: pytest, ruff, mypy, build
- Python version requirement: >=3.9

## [0.2] - 2017

### Added
- Initial release
- SGE script generation functionality
- Support for array jobs
- Cluster environment detection
