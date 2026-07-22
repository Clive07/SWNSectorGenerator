"""
Parametrized tests checking every data table for fields with no
meaningful value (null, blank, or empty), regardless of schema.
"""

import pytest

from helpers import describe_entry, find_invalid_fields
from swn_sector_generator.loading import RawTable

TABLE_FIXTURES = [
    "world_tags",
]


@pytest.mark.parametrize("table_fixture", TABLE_FIXTURES)
def test_table_has_no_invalid_fields(
    table_fixture: str, request: pytest.FixtureRequest
) -> None:
    """
    Verify that no entry in a data table has a null, blank, or empty field.

    Args:
        table_fixture: Name of the fixture providing raw table data.
        request: Pytest's fixture request, used to resolve the fixture by
            name so this test runs generically across tables.
    """
    table: RawTable = request.getfixturevalue(table_fixture)

    problem_entries = {
        describe_entry(tag, index): invalid_fields
        for index, tag in enumerate(table)
        if (invalid_fields := find_invalid_fields(tag))
    }

    assert not problem_entries, (
        "Found null, blank, or empty fields — review these entries and "
        "ensure every field has an actual value."
    )