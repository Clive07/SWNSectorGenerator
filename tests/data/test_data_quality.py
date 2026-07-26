"""
Parametrized tests checking every data table for fields with no
meaningful value (null, blank, or empty), regardless of schema.
"""

import pytest

from helpers import (describe_entry,
                     find_invalid_fields,
                     find_duplicate_field_values,
                     find_duplicate_list_items,
                     find_untrimmed_string_fields,
                     find_id_range_gaps,
                     )
from swn_sector_generator.loading import RawTable

TABLE_FIXTURES = [
    "world_tags",
]

TABLE_IDENTITY_FIELDS = [
    ("world_tags", ["id", "name"]),
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


@pytest.mark.parametrize("table_fixture, identity_fields", TABLE_IDENTITY_FIELDS)
def test_table_has_no_duplicate_identity_values(
        table_fixture: str, identity_fields: list[str], request: pytest.FixtureRequest
) -> None:
    """
    Verify no identity field (e.g. id, name) has duplicate values across the table.
    String values are compared case-insensitive.

    Args:
        table_fixture: Name of the fixture providing raw table data.
        identity_fields: List of fields that are expected to be unique.
        request: Pytest's fixture request, used to resolve the fixture by
            name so this test runs generically across tables.
    """
    table: RawTable = request.getfixturevalue(table_fixture)

    problem_fields = {
        field: duplicates
        for field in identity_fields
        if (duplicates := find_duplicate_field_values(table, field))
    }

    assert not problem_fields, (
        f"{table_fixture} YAML data file has duplicate values in fields that "
        "should be unique per entry. Each duplicated value below is mapped "
        "to the list positions (0-indexed) where it occurs in the file. "
        "i.e. 'id' {1: [1, 3] means the second and fourth entry in the file "
        "has the value 1 for it's id field."
    )


@pytest.mark.parametrize("table_fixture", TABLE_FIXTURES)
def test_table_entries_have_no_duplicate_list_items(
        table_fixture: str, request: pytest.FixtureRequest
) -> None:
    """
    Verify no entry's own list fields contain repeated items within themselves.
    String values are compared case-insensitive.

    Args:
        table_fixture: Name of the fixture providing raw table data.
        request: Pytest's fixture request, used to resolve the fixture by
            name so this test runs generically across tables.
    """

    table: RawTable = request.getfixturevalue(table_fixture)

    problem_entries = {
        describe_entry(tag, index): dupes
        for index, tag in enumerate(table)
        if (dupes := find_duplicate_list_items(tag))
    }

    assert not problem_entries, ("There are one or more entries in the "
                                 f"{table_fixture} YAML data file with "
                                 "duplicate list items."
                                 )


@pytest.mark.parametrize("table_fixture", TABLE_FIXTURES)
def test_table_has_no_untrimmed_string_fields(
    table_fixture: str, request: pytest.FixtureRequest
) -> None:
    """
    Verify that no entry has a string field with leading or trailing whitespace.

    Args:
        table_fixture: Name of the fixture providing raw table data.
        request: Pytest's fixture request, used to resolve the fixture by
            name so this test runs generically across tables.
    """
    table: RawTable = request.getfixturevalue(table_fixture)

    problem_entries = {
        describe_entry(tag, index): fields
        for index, tag in enumerate(table)
        if (fields := find_untrimmed_string_fields(tag))
    }

    assert not problem_entries, (
        f"{table_fixture} YAML data file has fields with leading or "
        "trailing whitespace that should be trimmed."
    )


@pytest.mark.parametrize("table_fixture", TABLE_FIXTURES)
def test_table_has_no_id_range_gaps(
    table_fixture: str, request: pytest.FixtureRequest
) -> None:
    """
    Verify a table's ids collectively cover 1 to its length, with
    nothing missing and nothing outside that expected range.

    Args:
        table_fixture: Name of the fixture providing raw table data.
        request: Pytest's fixture request, used to resolve the fixture by
            name so this test runs generically across tables.
    """
    table: RawTable = request.getfixturevalue(table_fixture)

    issues = find_id_range_gaps(table)

    assert not issues, (
        f"{table_fixture} YAML data file has id range issues - check "
        "for missing or mistyped id values."
    )