# Data Tables and Models

This project's game data (world tags, and eventually tech level,
population, atmosphere, etc.) is defined using three separate pieces per
table, each with a distinct job. This doc explains what each piece is for,
how they relate, and the conventions to follow when adding a new one.

## The three pieces

**YAML file** (`src/swn_sector_generator/resources/tables/<name>.yaml`) —
the actual data. A list of records, e.g. one entry per world tag.

**JSON Schema** (`src/swn_sector_generator/resources/tables/<name>.schema.json`) —
the runtime source of truth for what a valid record looks like: which
fields exist, which are required, and what type each one must be. Also
used directly by PyCharm to validate the YAML file while editing it.

**`TypedDict`** (`src/swn_sector_generator/models/<name>.py`) — a static
type describing the same shape, for code that consumes already-validated
data. Gives IDE autocomplete and mypy checking wherever a function
returns or accepts, say, a `WorldTag`, at zero runtime cost.

## Why three separate things, not one

It might seem redundant to describe the same shape three times. Each
piece exists because it serves a different consumer:

- The YAML file is edited by hand (or by a migration script).
- The JSON Schema is checked by PyCharm's editor tooling *while* editing,
  and by `jsonschema.validate()` at test time — both need a real,
  standalone schema document, not a Python type.
- The `TypedDict` is used by mypy and your IDE *while writing code* that
  handles this data — a JSON Schema file can't do that job, since it's
  not a Python type at all.

## The drift risk, and how it's guarded

Because the schema and the `TypedDict` are two handwritten descriptions
of the same shape, nothing stops them silently diverging over time —
someone could add a field to one and forget the other. This is guarded by
tests in `tests/data/test_schema_conformance.py`, which compare a
TypedDict's fields, required fields, and field types against its
schema, using Pydantic's `TypeAdapter` to generate a comparable schema
from the `TypedDict` itself. See the `test_schema_conformance.py` subsection of
[What each test file checks](testing.md#what-each-test-file-checks)
in `docs/testing.md` for details on how this works.

## Raw vs. validated data

Data fresh off disk (via `yaml.safe_load`/`json.load`) is untyped and
unvalidated — it's just whatever was in the file, correct or not. This is
represented by `RawEntry` (`dict[str, Any]`) and `RawTable`
(`list[RawEntry]`), defined in `src/swn_sector_generator/loading.py`.

Right now, `RawTable`/`RawEntry` are only used by the test suite, to load
each table's data for schema and data-quality checks. No application code
yet performs the "load raw data, validate it, produce real `WorldTag`
instances" step as a runtime feature — that's a piece of the eventual
`services/` layer, not something that exists today.

Once that loader exists, it's the boundary where `RawTable`/`RawEntry`
give way to real TypedDicts. A `TypedDict` like `WorldTag` should only
ever describe data that's already been validated, so code past that
boundary should be typed `list[WorldTag]`, not `RawTable`. Whether that
future loader is one generic function per table, a single function
covering several tables via a type parameter, or something else, is an
open design question for when the `services/` layer is actually built —
not something to decide here.

## Naming conventions

- **YAML/schema files are plural** (`world_tags.yaml`) — they hold a
  collection of records.
- **Model modules and classes are singular** (`models/world_tag.py`,
  `class WorldTag`) — each describes the shape of *one* record.

## `TypedDict` today, Pydantic eventually

`TypedDict` is deliberately being used for now rather than a full
Pydantic model. It gives static typing with zero runtime cost, which
matches the project's current stage — nothing yet needs Pydantic's
runtime validation or FastAPI integration. Introducing Pydantic now would
be premature complexity for validation that the JSON Schema tests already
provide at the test level.

When the migration does happen, code using dict-style access
(`world_tag["name"]`) will need to change to attribute-style access
(`world_tag.name`), since a `TypedDict` is still a plain `dict` at
runtime while a Pydantic model is a real object. The `test_schema_conformance.py`
drift-guard tests should keep working with minimal changes at that point,
since `TypeAdapter` accepts Pydantic models as readily as `TypedDict`s —
and Pydantic models can generate their own JSON Schema directly via
`model_json_schema()`, which could eventually replace hand-maintaining
the schema file at all, removing the drift risk rather than just
detecting it.

## Adding a new table

See [Adding a new table](testing.md#adding-a-new-table) in `docs/testing.md` for the 
test-side checklist.
On the data-modelling side, a new table needs:

1. `src/swn_sector_generator/resources/tables/<name>.yaml` — the data.
2. `src/swn_sector_generator/schemas/<name>.schema.json` — its
   schema, following the same conventions as `world_tags.schema.json`
   (`type: array`, `items` describing one record, `additionalProperties:
   false`, explicit `required`).
3. `src/swn_sector_generator/models/<name>.py` — a `TypedDict` describing
   the same shape.