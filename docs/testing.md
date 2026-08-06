# Testing

This project's tests validate the raw YAML data tables and their supporting
types (JSON Schemas and TypedDicts). This doc explains how the test suite
is structured, the conventions it follows, and how to extend it to a new
data table.

## Running the tests

```bash
pytest
```

Configuration lives entirely in `pyproject.toml` under
`[tool.pytest.ini_options]`:

- `--import-mode=importlib` — avoids filename collisions between test files
  in different subfolders, without needing `__init__.py` files anywhere
  under `tests/`.
- `pythonpath = ["tests"]` — lets test files import shared helpers
  (`tests/helpers.py`) as a plain module, from any subfolder under `tests/`.
- `--cov-fail-under=80` — coverage is measured, missing lines are
  reported, and the run fails outright if coverage drops below 80%.
  The auto-generated `_version.py` is excluded from this measurement
  — see [Coverage configuration](tooling.md#coverage-configuration).
- `-vv` — disables pytest's default truncation of large assertion output,
  so a failing test listing many problem entries shows all of them in one
  run rather than requiring a re-run to see the rest.

The full suite also runs automatically before every `git push`, via a
pre-commit hook — see [tooling.md](tooling.md#pre-commit-hooks)
for the full pre-commit setup.

## Directory layout

```text
tests/
├── conftest.py       # fixtures for loading each table's YAML and schema
├── helpers.py        # shared validation helper functions
├── test_helpers.py    # tests for helpers.py itself
└── data/
    ├── test_schema_conformance.py   # tables and TypedDicts vs. their schemas
    ├── test_data_quality.py        # generic content checks (blank, duplicate, etc.)
```

## The core pattern: generic checks, parametrized per table

Every data table is expected to follow the same shape (a list of records,
each with a paired JSON Schema and `TypedDict`). Rather than writing one
near-identical test per table, most checks are written once, generically,
and run against every table via `@pytest.mark.parametrize`.

A generic test typically looks like:

```python
@pytest.mark.parametrize("table_fixture", TABLE_FIXTURES)
def test_table_has_no_invalid_fields(
    table_fixture: str, request: pytest.FixtureRequest
) -> None:
    table: RawTable = request.getfixturevalue(table_fixture)
    ...
    assert not problem_entries, "..."
```

`request.getfixturevalue(table_fixture)` resolves a fixture by name at
runtime, which is what allows one test function to run once per table
listed in `TABLE_FIXTURES`, each getting that table's own data.

Adding a new table to any of these generic checks means adding its fixture
name to a list — no new test logic required. See [Adding a new table](#adding-a-new-table)
below.

Tests also follow a few ruff-enforced style conventions (parametrize
formatting, assertion structure) — see
[Linting conventions enforced](tooling.md#linting-conventions-enforced)
in tooling.md for the full list.

## Fixtures (`conftest.py`)

Each table gets two session-scoped fixtures, built by small factory
functions rather than one pair per table written by hand:

- `_make_table_fixture(table_name)` — loads `<table_name>.yaml` from the
  resources directory, returning a `RawTable` (see `loading.py`).
- `_make_schema_fixture(table_name)` — loads `<table_name>.schema.json`
  from the schemas directory, returning a `RawSchema`.

Fixtures are session-scoped (`scope="session"`) since the underlying files
don't change during a test run — this avoids re-reading and reparsing the
same file for every test that needs it.

`RawTable` and `RawEntry` (a list of records, and one record, respectively)
live in `src/swn_sector_generator/loading.py`, not in `conftest.py` or
`tests/helpers.py`. They're imported from the installed package rather
than defined locally, so they're reliably importable from any test file
regardless of pytest's import mode or folder structure.

## What each test file checks

**`test_schema_conformance.py`** — structural correctness:

- The raw table data actually validates against its JSON Schema
  (`jsonschema.validate`).
- The corresponding `TypedDict`'s fields, required fields, and field types
  haven't drifted out of sync with the schema. The schema is the runtime
  source of truth; the `TypedDict` is a static-typing aid for code that
  consumes already-validated data — nothing enforces they stay in sync
  automatically, so this test exists specifically to catch that drift.
  Field-type comparison uses Pydantic's `TypeAdapter(SomeTypedDict).json_schema()`
  to generate a comparable schema from the `TypedDict`, rather than a
  hand-rolled Python-type-to-JSON-Schema mapping.

**`test_data_quality.py`** — content correctness, independent of schema
validity (a value can be the right *type* and still be a data-quality
problem):

- No null, blank, or empty required fields (`find_invalid_fields`).
- No leading/trailing whitespace on string values, including inside lists
  (`find_untrimmed_string_fields`).
- No duplicate values in identity fields like `id`/`name` across the whole
  table (`find_duplicate_field_values`) — compared case-insensitively,
  since a capitalisation-only difference is almost always a typo.
- No duplicate items within a single entry's own list fields
  (`find_duplicate_list_items`) — also case-insensitive. Note: the same
  item repeating *across different entries* (e.g. two world tags both
  listing "Pirates" as an enemy) is expected and not checked — only
  repeats *within one entry's own list* are a problem.
- `id` values collectively cover `1..N` with nothing missing or
  unexpected (`find_id_range_gaps`). This does **not** check that entries
  appear in `id` order within the file — file ordering is a cosmetic
  concern with no bearing on correctness, and isn't enforced by a test.

## `helpers.py`

Shared functions used across the generic checks above. Notable ones:

- `describe_entry(entry, index)` — builds a human-readable label for an
  entry in failure messages, falling back from `name`, to `id`, to the
  entry's list index, since either of the first two might itself be
  missing or blank.
- `_normalise_for_comparison(value)` — case-folds strings for
  case-insensitive comparison, leaving non-string values (e.g. `id`
  integers) untouched. Shared by both duplicate-detection functions.
- `_is_blank_string(value)` — shared by the blank-field and
  untrimmed-string checks.

Functions prefixed with `_` are internal — only called by other functions
in this module, not directly by test files. They're still tested directly
in `test_helpers.py`; the underscore signals "not part of this module's
public surface," not "untested."

## Adding a new table

Once a new table's `<name>.yaml`, `<name>.schema.json`, and `TypedDict`
exist:

1. **`conftest.py`** — add its
   `_make_table_fixture`/`_make_schema_fixture` pair.
2. **`test_schema_conformance.py`** — add `(table_fixture, schema_fixture,
   TypedDict)` to `TABLE_DEFINITIONS`.
3. **`test_data_quality.py`** — add the table's fixture name to
   `TABLE_FIXTURES`, and add `(table_fixture, identity_fields)` to
   `TABLE_IDENTITY_FIELDS`, confirming which fields (e.g. `id`, `name`)
   are expected to be unique for that table.

No new test functions should be needed for any of the generic checks —
only for anything genuinely unique to that table.
