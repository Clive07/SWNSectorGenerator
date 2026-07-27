# SWN Sector Generator

A tool for generating and managing sectors for the tabletop RPG *Stars
Without Number*. Currently a data/backend-focused hobby project, with a
GUI and Neo4j-backed persistence planned.

## Status

Early stage. Core game data (world tags, and eventually tech level,
population, atmosphere, and more) is being modelled as YAML tables,
validated against JSON Schemas, with a test suite covering both
structural and data-quality checks. See [docs](docs/index.md) for
details.

## Tech stack

- **Python 3.14**
- **YAML** for game data tables, validated against **JSON Schema**
- **pytest** / **pytest-cov** for testing (minimum 80% coverage)
- **ruff** for linting and formatting
- **PySide/PyQt** for the GUI (planned)
- **Neo4j** (free edition) for persistence (planned)

`pyproject.toml` is the single configuration file for packaging, linting,
and test settings.

## Getting started

```
pip install -e .[dev]
```

This installs the project itself along with its runtime dependencies
(currently PyYAML), plus the `[dev]` extra: additional dependencies
needed only for development and testing (pytest, ruff, jsonschema,
pydantic).

## Running the tests

```
pytest
```

Configuration in `pyproject.toml` means this also enforces a minimum 80%
coverage, reports full (non-truncated) failure detail, and requires no
extra setup for importing test-only helper modules. See
[testing.md](docs/testing.md) for how the suite is structured.

## Documentation

See [index.md](docs/index.md) for the full list of technical docs,
covering the test suite and the data table/model architecture.