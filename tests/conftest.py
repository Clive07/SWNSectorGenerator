"""
Fixtures used by the test files.
"""

import json
from pathlib import Path
from typing import Callable

import pytest
import yaml

from swn_sector_generator.loading import RawTable, RawSchema

PROJECT_DIR = Path(__file__).parent.parent
TABLES_DIR = PROJECT_DIR / "src" / "swn_sector_generator" / "resources" / "tables"
SCHEMAS_DIR = PROJECT_DIR / "schemas"




def _load_yaml_table(file_path: Path) -> RawTable:
    """
    Load a YAML data table from disk.

    Args:
        file_path: Path to the YAML file.

    Returns:
        The raw list of records parsed from the file.
    """
    with file_path.open(mode="r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _load_json_schema(file_path: Path) -> RawSchema:
    """
    Load a JSON Schema document from disk.

    Args:
        file_path: Path to the JSON Schema file.

    Returns:
        The parsed JSON Schema document.
    """
    with file_path.open(mode="r", encoding="utf-8") as file:
        return json.load(file)


def _make_table_fixture(table_name: str) -> Callable[[], RawTable]:
    """
    Build a session-scoped fixture that loads one YAML data table.

    Args:
        table_name: Base filename of the table, without extension
            (e.g. "world_tags").

    Returns:
        A pytest fixture function that yields the table's raw records.
    """

    @pytest.fixture(scope="session")
    def _fixture() -> RawTable:
        return _load_yaml_table(TABLES_DIR / f"{table_name}.yaml")

    return _fixture


def _make_schema_fixture(table_name: str) -> Callable[[], RawSchema]:
    """
    Build a session-scoped fixture that loads one table's JSON Schema.

    Args:
        table_name: Base filename of the schema, without extension
            (e.g. "world_tags").

    Returns:
        A pytest fixture function that yields the parsed schema.
    """

    @pytest.fixture(scope="session")
    def _fixture() -> RawSchema:
        return _load_json_schema(SCHEMAS_DIR / f"{table_name}.schema.json")

    return _fixture


# --- Table fixtures ---------------------------------------------------

world_tags = _make_table_fixture("world_tags")
world_tags_schema = _make_schema_fixture("world_tags")
