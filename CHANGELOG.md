# Changelog

## [0.3.0] - 2026-08-07

### 🐛 Bug Fixes

- *(changelog)* Correct cliff.toml generation and grouping issues

### 📚 Documentation

- Refresh documentation for pre-commit and tooling changes

### 🎨 Styling

- *(pyproject)* Reorder sections to fit convention
- Apply ruff and mypy fixes across schemas, src and tests

### 🧪 Testing

- *(coverage)* Exclude _version.py from coverage

### ⚙️ Miscellaneous Tasks

- *(git)* Set default line terminator for text files to LF
- *(config)* Set up configurations for dev linting tools
- *(config)* Add gitlint for commit message linting
- *(config)* Configure pre-commit hooks
- *(config)* Set up mypy to be used effectively
- Add GitHub Actions workflow for linting and tests
- *(git)* Ignore mypy and ruff cache directories

## [0.2.0] - 2026-07-28

### 🚀 Features

- *(world-tags)* Add attributes for first 40 tags and update description
  minimum length to 1
- *(world-tags)* Add attributes for remaining 60 tags
- *(loading)* Add type aliases for raw pre-validation data
- *(models)* Add WorldTag TypedDict for world tag entries

### 🐛 Bug Fixes

- *(changelog)* Correct security grouping and skip merge commits

### 📚 Documentation

- Add testing and data-tables tech docs, update README
- *(changelog)* Add v0.2.0 release notes

### 🎨 Styling

- Apply ruff formatting across the codebase

### 🧪 Testing

- *(conftest)* Add session-scoped fixtures for loading raw table and schema data
- *(data)* Add schema conformance tests for tables and TypedDicts
- *(data)* Add generic data quality checks across all tables
- *(data)* Add tests for finding duplicate values in data files
- *(data)* Add whitespace check and make duplicate checks case-insensitive
- *(data)* Add test for checking id range gaps

### ⚙️ Miscellaneous Tasks

- *(build)* Switch to dynamic versioning via setuptools-scm
- *(changelog)* Add git-cliff config and generate initial changelog
- *(pytest)* Configure import mode and coverage options

## [0.1.1] - 2026-07-17

### 🚀 Features

- *(schema)* Add description field to world tag schema, flip things and
  complications around
- *(data)* Migrate world tags and add initial content

### 🛡️ Security

- *(deps)* Update pytest to fix security vulnerability

### ⚙️ Miscellaneous Tasks

- *(scripts)* Add world tag migration utility
- *(version)* Bump package version to 0.1.1

## [0.1.0] - 2026-07-16

### 🚀 Features

- *(world-tags)* Introduce world tag schema and initial tags

### ⚙️ Miscellaneous Tasks

- *(git)* Initialise repository configuration
- *(git)* Configure repository ignore rules
- *(project)* Configure python package structure
