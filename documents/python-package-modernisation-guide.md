# Modern Python Package Structure: A Complete Guide

## Introduction

Python packaging has matured significantly over the past decade. What was once a fragmented landscape of competing approaches has consolidated around clear, standardised practices. This guide explains not just *what* to do when modernising your packages, but *why* these structures exist and how they serve both you and your users.

## Understanding Python Packaging Fundamentals

### Why Packaging Matters

At its core, packaging solves a deceptively simple problem: how do we share Python code reliably? When you write a collection of Python modules, several questions arise:

- How do others install your code on their systems?
- How do we specify which other packages your code depends upon?
- How do we ensure your code works across different Python versions?
- How do we describe what your package does and who maintains it?

The packaging ecosystem exists to answer these questions systematically. When done properly, users can install your package with a single command, confident that all dependencies will be resolved and the code will work as intended.

### The Evolution to pyproject.toml

Python packaging historically relied on `setup.py` files—executable Python scripts that described how to build and install packages. Whilst functional, this approach had significant drawbacks:

**Security concerns**: Executing arbitrary Python code during installation created potential attack vectors. Build tools had to run untrusted code before they could even understand a package's requirements.

**Inconsistency**: Different tools interpreted `setup.py` differently, leading to subtle incompatibilities. There was no guarantee that a package built with one tool would work properly with another.

**Complexity**: Simple tasks required understanding Python packaging internals. Declaring dependencies meant learning setuptools' specific API rather than simply listing requirements.

The solution emerged through a series of Python Enhancement Proposals (PEPs):

- **PEP 518** (2016) introduced `pyproject.toml` as a declarative configuration file
- **PEP 517** defined how build tools should interact with projects
- **PEP 621** (2020) standardised project metadata format

This progression represents a philosophical shift: packaging configuration should be *declarative* (stating what you need) rather than *imperative* (describing how to build). The `pyproject.toml` file uses TOML format—human-readable, unambiguous, and requiring no code execution to parse.

### How Package Installation Works

Understanding the installation process illuminates why modern structure matters:

1. **Discovery**: A package manager (pip, uv) locates your package on PyPI or locally
2. **Metadata extraction**: The tool reads `pyproject.toml` to understand requirements
3. **Dependency resolution**: All required packages and their versions are determined
4. **Build preparation**: If needed, a temporary environment with build tools is created
5. **Wheel creation**: Your package is compiled into a wheel (a standardised distribution format)
6. **Installation**: The wheel's contents are copied to the appropriate site-packages directory

Modern packaging separates these concerns cleanly. The `[build-system]` table tells tools what's needed to *build* your package, whilst the `[project]` table describes the package itself and what it needs to *run*.

## Package Structure Rationale

### The src Layout Philosophy

Modern Python packages overwhelmingly favour the "src layout" over flat structures. The reasoning is subtle but important:

```
project-root/
├── src/
│   └── package_name/
│       ├── __init__.py
│       └── modules.py
├── tests/
├── docs/
└── pyproject.toml
```

**Why this structure?** It solves a fundamental Python behaviour: when you run Python in a directory, that directory is automatically added to the module search path. With a flat layout, if your package directory sits at the project root, Python will import from your source files directly rather than from the installed package.

This creates a dangerous disconnect: your tests might pass locally whilst importing from source files, but fail for users who've installed the package properly. You might accidentally depend on files that aren't included in the distribution. The src layout forces an honest test—if the package isn't installed, imports fail immediately.

Additional benefits emerge from this separation:

- **Clean namespace**: Project-level configuration files don't clutter the package namespace
- **Clear boundaries**: What's source code versus what's tooling becomes obvious
- **Distribution clarity**: Only contents of `src/` get packaged, preventing accidental inclusion of development files

### Understanding __init__.py

Every package directory requires an `__init__.py` file, even if empty. This file serves two purposes:

1. **Package marker**: It signals to Python that this directory is a package, not just a collection of scripts
2. **Initialisation**: Code in `__init__.py` executes when the package is imported, allowing you to control the public API

For example:

```python
# src/mypackage/__init__.py
from .core import main_function
from .utils import helper

__version__ = "1.0.0"
__all__ = ['main_function', 'helper']
```

This lets users write `from mypackage import main_function` rather than `from mypackage.core import main_function`, creating a cleaner API.

### Tests Directory

Tests live outside `src/` in their own `tests/` directory:

```
project-root/
├── src/
│   └── mypackage/
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_utils.py
└── pyproject.toml
```

This placement serves several purposes:

- **Distribution size**: Tests aren't included in the installed package, reducing download size
- **Clear separation**: Development tools versus production code remain distinct
- **Proper testing**: Tests run against the installed package, not source files

Test files should mirror the package structure (`test_core.py` tests `core.py`) and use clear naming conventions.

## The pyproject.toml File

This file is your package's single source of truth. Let's examine each section's purpose:

### Build System Declaration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

This section answers two critical questions:

1. **What tools are needed to build this package?** The `requires` list specifies build-time dependencies
2. **Which build backend should be used?** The `build-backend` specifies the tool that will create wheels

Think of this as a bootstrapping mechanism: before anything else can happen, these tools must be available.

**Choosing a build backend:**

- **Hatchling**: Modern, fast, minimal configuration. Excellent for pure Python packages
- **Setuptools**: Most mature option, necessary for packages with C extensions or complex builds
- **Flit**: Extremely simple, good for small pure Python packages
- **PDM-backend**: Modern alternative with good PEP 621 support

For most packages, Hatchling represents the best balance of simplicity and capability.

### Project Metadata

```toml
[project]
name = "my-package"
version = "1.0.0"
description = "A brief, clear description"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["relevant", "keywords"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "requests>=2.28.0",
    "numpy>=1.24.0,<2.0",
]
```

Let's examine each field's purpose:

**name**: Your package's identifier on PyPI. Use lowercase with hyphens. This can differ from the import name (which uses underscores).

**version**: Semantic versioning (MAJOR.MINOR.PATCH) tells users about compatibility. Increment major for breaking changes, minor for new features, patch for bug fixes.

**description**: A single-line summary appearing in search results. Make it clear and specific.

**readme**: Points to your README file. This becomes your PyPI project description. Use Markdown for formatting.

**requires-python**: Specifies minimum Python version. This helps package managers avoid installing your package where it won't work.

**license**: Critical for users to understand usage rights. Use SPDX identifiers or reference a LICENSE file.

**authors**: Helps users identify maintainers. Email is optional but recommended.

**keywords**: Improves discoverability on PyPI. Choose terms users might search for.

**classifiers**: Structured metadata for filtering on PyPI. These indicate development status, intended audience, license, and supported Python versions. Browse the [full list](https://pypi.org/classifiers/) when setting these.

**dependencies**: Runtime requirements. Use version specifiers thoughtfully:
- `>=2.0.0`: Minimum version (allows any newer version)
- `>=2.0,<3.0`: Version range (major version constraint)
- `~=2.1.0`: Compatible release (equivalent to `>=2.1.0,<2.2.0`)

### Optional Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]
docs = [
    "sphinx>=7.0",
    "sphinx-rtd-theme>=2.0",
]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
```

Optional dependencies support different use cases:

- **dev**: Tools for development (linters, formatters, type checkers)
- **test**: Testing frameworks and related tools
- **docs**: Documentation building tools
- **extras**: Additional features users can opt into

Users install these with: `pip install mypackage[dev]` or `uv sync --group dev`

This separation keeps the base install lean whilst supporting comprehensive development.

### Scripts and Entry Points

```toml
[project.scripts]
mycommand = "mypackage.cli:main"

[project.gui-scripts]
myapp = "mypackage.gui:launch"
```

Scripts create command-line tools. When users install your package, these commands become available in their PATH.

The format `module.submodule:function` tells Python exactly which function to call. Console scripts attach to terminal, GUI scripts (Windows) run without a console window.

### URLs

```toml
[project.urls]
Homepage = "https://github.com/username/package"
Documentation = "https://package.readthedocs.io"
Repository = "https://github.com/username/package"
"Bug Tracker" = "https://github.com/username/package/issues"
Changelog = "https://github.com/username/package/blob/main/CHANGELOG.md"
```

These links appear on your PyPI page, helping users find resources. Include at minimum your repository and documentation.

### Tool Configuration

Modern tools can be configured in the same file:

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
strict = true
```

This centralisation reduces configuration sprawl and makes tool settings discoverable.

## Working with uv

The uv package manager works seamlessly with standard `pyproject.toml` files. It brings several advantages:

**Speed**: Written in Rust, uv resolves dependencies and installs packages 10-100× faster than traditional tools.

**Reproducibility**: uv generates a `uv.lock` file capturing exact dependency versions, ensuring consistent environments.

**Simplicity**: Combines environment management, dependency resolution, and package installation in one tool.

**Compatibility**: Works with any PEP 621-compliant `pyproject.toml`, making it a drop-in replacement.

### Key uv Concepts

**Lock files**: `uv.lock` records exact versions of all dependencies. Commit this to version control for reproducible builds. Never edit it manually—uv manages it automatically.

**Python version management**: uv can install and manage Python versions via `.python-version` files, ensuring teams use consistent Python versions.

**Development workflow**:
```bash
uv sync              # Install dependencies and create environment
uv add requests      # Add a new dependency
uv remove requests   # Remove a dependency
uv run pytest        # Run commands in the project environment
uv build             # Build distribution files
```

The `uv sync` command is particularly powerful—it ensures your environment matches your `pyproject.toml` and `uv.lock` files, installing missing packages and removing orphaned ones.

## File Structure Essentials

### Complete Modern Package Layout

```
mypackage/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── core.py
│       ├── utils.py
│       └── data/
│           └── config.json
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_utils.py
├── docs/
│   ├── conf.py
│   ├── index.rst
│   └── api.rst
├── .gitignore
├── .python-version
├── LICENSE
├── README.md
├── CHANGELOG.md
├── pyproject.toml
└── uv.lock
```

### Key Files Explained

**.gitignore**: Prevents committing generated files, virtual environments, and build artifacts. Use a Python-specific template.

**.python-version**: Specifies the Python version for this project. uv uses this to ensure correct Python version.

**LICENSE**: Essential for open source. Choose an appropriate license (MIT, Apache 2.0, GPL) and include the full text.

**README.md**: Your package's front door. Should include:
- Clear description of what the package does
- Installation instructions
- Quick start examples
- Link to documentation
- Contribution guidelines

**CHANGELOG.md**: Documents changes between versions. Follow [Keep a Changelog](https://keepachangelog.com/) format for consistency.

### Package Data

If your package includes non-Python files (configuration, data files), place them within the package structure and reference them properly:

```python
from importlib.resources import files
import json

config_text = files('mypackage').joinpath('data/config.json').read_text()
config = json.loads(config_text)
```

This approach works across different installation methods and is more reliable than path manipulation.

## Naming Conventions

Python has strong naming conventions that improve code readability:

**Package/module names**: lowercase with underscores (`my_package`)
**Class names**: PascalCase (`MyClass`)
**Function/variable names**: lowercase with underscores (`calculate_total`)
**Constants**: uppercase with underscores (`MAX_CONNECTIONS`)

For PyPI, package names use hyphens (`my-package`), but the import name uses underscores (`import my_package`). This separation is standard practice.

## Version Management

Version numbers convey important information through [Semantic Versioning](https://semver.org/):

**MAJOR.MINOR.PATCH** where:
- **MAJOR**: Increment for incompatible API changes
- **MINOR**: Increment for backwards-compatible functionality additions
- **PATCH**: Increment for backwards-compatible bug fixes

For pre-release versions:
- Development: `1.0.0.dev0`, `1.0.0.dev1`
- Alpha: `1.0.0a1`, `1.0.0a2`
- Beta: `1.0.0b1`, `1.0.0b2`
- Release candidates: `1.0.0rc1`, `1.0.0rc2`

Consider using `setuptools-scm` to derive versions from git tags automatically:

```toml
[build-system]
requires = ["setuptools>=64", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
```

This eliminates manual version updates—simply tag releases in git: `git tag v1.0.0`

---

## Package Modernisation Checklist

### Phase 1: Structure Assessment

- [ ] Identify current package structure (flat vs src layout)
- [ ] Locate existing configuration files (`setup.py`, `setup.cfg`, `requirements.txt`)
- [ ] Document current dependencies and their versions
- [ ] Review existing tests and their location
- [ ] Note any C extensions or special build requirements
- [ ] Check for data files or package resources
- [ ] Identify Python version requirements

### Phase 2: Create New Structure

#### Directory Setup

- [ ] Create `src/` directory in project root
- [ ] Create `src/packagename/` directory (use underscores, not hyphens)
- [ ] Move package code into `src/packagename/`
- [ ] Ensure `__init__.py` exists in all package directories
- [ ] Create or verify `tests/` directory at project root
- [ ] Create `docs/` directory if documentation exists
- [ ] Add `.python-version` file specifying Python version

#### Essential Files

- [ ] Create `pyproject.toml` at project root
- [ ] Create or update `README.md` with clear description and usage
- [ ] Add `LICENSE` file with appropriate license text
- [ ] Create `CHANGELOG.md` to track version history
- [ ] Add comprehensive `.gitignore` for Python projects

### Phase 3: Configure pyproject.toml

#### Build System

- [ ] Add `[build-system]` section
- [ ] Choose build backend (hatchling recommended for pure Python)
- [ ] Specify backend requirements

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### Core Metadata

- [ ] Set package `name` (lowercase, hyphens for PyPI)
- [ ] Set initial `version` following semantic versioning
- [ ] Write clear, concise `description`
- [ ] Reference `readme` file
- [ ] Specify `requires-python` minimum version
- [ ] Add `license` information
- [ ] List `authors` with names and emails
- [ ] Add relevant `keywords`
- [ ] Include comprehensive `classifiers`

#### Dependencies

- [ ] List runtime `dependencies` from requirements.txt
- [ ] Use appropriate version specifiers (`>=`, `~=`, `<`)
- [ ] Create `[project.optional-dependencies]` groups:
  - [ ] `dev` for development tools
  - [ ] `test` for testing frameworks
  - [ ] `docs` for documentation tools
  - [ ] Any feature-specific extras

#### URLs and Entry Points

- [ ] Add `[project.urls]` for homepage, repository, documentation
- [ ] Define `[project.scripts]` if package provides CLI tools
- [ ] Add `[project.gui-scripts]` if applicable

#### Tool Configuration

- [ ] Add `[tool.pytest.ini_options]` if using pytest
- [ ] Add `[tool.ruff]` configuration if using Ruff
- [ ] Add `[tool.mypy]` settings if using type checking
- [ ] Configure other tools in `[tool.toolname]` sections

### Phase 4: Build Backend Specific Configuration

#### If using setuptools:

```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["packagename*"]
exclude = ["tests*"]
```

#### If using hatchling:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/packagename"]
```

### Phase 5: Update Tests

- [ ] Move tests to `tests/` directory if not already there
- [ ] Update import statements to use package name
- [ ] Add `__init__.py` to tests directory
- [ ] Configure test discovery in `pyproject.toml`
- [ ] Add test dependencies to `[project.optional-dependencies]`
- [ ] Verify tests pass with new structure

### Phase 6: Update Code References

- [ ] Update relative imports to absolute imports where appropriate
- [ ] Fix any imports broken by structure change
- [ ] Update `__init__.py` to expose public API
- [ ] Set `__version__` in `__init__.py` or use dynamic versioning
- [ ] Update any hard-coded paths to use `importlib.resources`
- [ ] Review and update docstrings

### Phase 7: Development Environment Setup

#### With uv:

- [ ] Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Create `.python-version` file with desired Python version
- [ ] Run `uv sync` to create environment and install dependencies
- [ ] Verify `uv.lock` is created
- [ ] Add `uv.lock` to version control
- [ ] Test package installation: `uv run python -c "import packagename"`

#### With pip:

- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate environment
- [ ] Install in editable mode: `pip install -e ".[dev]"`
- [ ] Verify installation works

### Phase 8: Documentation Updates

- [ ] Update README.md with:
  - [ ] Clear description
  - [ ] Installation instructions using `pip install` or `uv add`
  - [ ] Quick start examples
  - [ ] Link to full documentation
  - [ ] Contribution guidelines
- [ ] Create or update CHANGELOG.md with version history
- [ ] Update any existing documentation for new structure
- [ ] Add docstrings to all public functions and classes

### Phase 9: CI/CD Updates

- [ ] Update CI pipeline to use modern package structure
- [ ] Configure CI to test against multiple Python versions
- [ ] Update deployment scripts for new build process
- [ ] Test building distributions: `python -m build` or `uv build`
- [ ] Verify wheel contents are correct

### Phase 10: Clean-up

- [ ] Remove `setup.py` if no longer needed
- [ ] Remove `setup.cfg` if migrated to `pyproject.toml`
- [ ] Remove `requirements.txt` if migrated to `pyproject.toml`
- [ ] Remove `MANIFEST.in` if no longer needed (usually unnecessary with modern backends)
- [ ] Clean up any legacy configuration files
- [ ] Update `.gitignore` to exclude:
  - [ ] `*.pyc` and `__pycache__/`
  - [ ] `.venv/`, `venv/`, `env/`
  - [ ] `dist/`, `build/`, `*.egg-info/`
  - [ ] `.pytest_cache/`, `.coverage`, `.mypy_cache/`
  - [ ] IDE-specific files (`.vscode/`, `.idea/`)

### Phase 11: Testing and Validation

- [ ] Run test suite: `uv run pytest` or `pytest`
- [ ] Verify all tests pass
- [ ] Run linters: `ruff check .`
- [ ] Run type checker: `mypy src/`
- [ ] Build distributions: `uv build` or `python -m build`
- [ ] Check distribution contents: `tar -tzf dist/*.tar.gz`
- [ ] Test installation from wheel: `pip install dist/*.whl`
- [ ] Test CLI tools if applicable
- [ ] Verify package imports correctly: `python -c "import packagename"`

### Phase 12: Publication Preparation

- [ ] Create PyPI account at https://pypi.org
- [ ] Generate API token for uploads
- [ ] Configure token in: `~/.pypirc` or use `uv publish` authentication
- [ ] Test upload to TestPyPI first: `uv publish --publish-url https://test.pypi.org/legacy/`
- [ ] Verify package appears correctly on TestPyPI
- [ ] Install from TestPyPI and test: `pip install --index-url https://test.pypi.org/simple/ packagename`

### Phase 13: Release

- [ ] Update version in `pyproject.toml` (or git tag if using setuptools-scm)
- [ ] Update CHANGELOG.md with release notes
- [ ] Commit all changes
- [ ] Create git tag: `git tag v1.0.0`
- [ ] Push with tags: `git push --tags`
- [ ] Build fresh distributions: `uv build`
- [ ] Upload to PyPI: `uv publish`
- [ ] Verify package on PyPI
- [ ] Test installation: `pip install packagename`
- [ ] Create GitHub release with notes

### Phase 14: Documentation

- [ ] Add migration notes to CHANGELOG
- [ ] Update contribution guidelines for new structure
- [ ] Document development setup process
- [ ] Note any breaking changes from restructure
- [ ] Update any existing tutorials or examples

---

## Quick Reference: Essential pyproject.toml Template

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "package-name"  # PyPI name (hyphens)
version = "0.1.0"
description = "A concise description of your package"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["keyword1", "keyword2", "keyword3"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "requests>=2.28.0",
    "numpy>=1.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
    "mypy>=1.0",
]
docs = [
    "sphinx>=7.0",
    "sphinx-rtd-theme>=2.0",
]

[project.urls]
Homepage = "https://github.com/username/package"
Documentation = "https://package.readthedocs.io"
Repository = "https://github.com/username/package"
"Bug Tracker" = "https://github.com/username/package/issues"

[project.scripts]
package-cli = "package_name.cli:main"

# Tool configurations
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
exclude = [".venv", "build", "dist"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

---

## Common Pitfalls and Solutions

### Import Errors After Restructuring

**Problem**: Tests fail with `ModuleNotFoundError` after moving to src layout.

**Solution**: Install package in editable mode: `pip install -e .` or `uv sync`. Tests must import from the installed package, not source files.

### Package Not Found When Building

**Problem**: Build tools can't find your package in `src/`.

**Solution**: Configure package discovery in `pyproject.toml`:

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

Or with hatchling:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/packagename"]
```

### Dependencies Not Installing

**Problem**: Runtime dependencies don't install with package.

**Solution**: Ensure dependencies are in `[project]` section's `dependencies` array, not `[project.optional-dependencies]`.

### Version Conflicts

**Problem**: Package version conflicts with dependencies.

**Solution**: Use flexible version specifiers. Prefer `>=` over `==` unless specific version required. Use upper bounds cautiously: `package>=1.0,<2.0` if needed.

### Missing Data Files

**Problem**: Package data files not included in distribution.

**Solution**: Place data within package structure (`src/package/data/`). Use `importlib.resources` to access, not file paths.

### Incorrect Package Name

**Problem**: Can't install or import package due to name mismatch.

**Solution**: 
- PyPI name (in `pyproject.toml`): Use hyphens (`my-package`)
- Directory name in `src/`: Use underscores (`my_package`)
- Import statement: Matches directory name (`import my_package`)

---

## Conclusion

Modern Python packaging represents years of community learning distilled into clear standards. The `pyproject.toml` file, src layout, and tools like uv work together to make packaging more reliable, secure, and maintainable.

The investment in restructuring aging packages pays dividends:
- **For maintainers**: Simpler configuration, better testing, easier releases
- **For users**: Reliable installation, clear dependencies, consistent behaviour
- **For the ecosystem**: Interoperable tools, shared understanding, reduced fragmentation

By following these patterns, you're not just updating your packages—you're participating in a collective effort to make Python packaging better for everyone.

## Further Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 621 – Storing project metadata](https://peps.python.org/pep-0621/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Choose a License](https://choosealicense.com/)
- [PyPI Classifiers List](https://pypi.org/classifiers/)

---

*Guide version: 1.0*  
*Last updated: October 2025*
