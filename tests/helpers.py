"""
Shared helper functions for validating raw table data across test files.
"""

from typing import Any

from swn_sector_generator.loading import RawTable, RawEntry


def _is_blank_string(value: Any) -> bool:
    """
    Determine whether a value is a string that's empty or whitespace-only.

    Args:
        value: The value to check.

    Returns:
        True if value is a string with no meaningful content.
        False otherwise.
    """

    return isinstance(value, str) and not value.strip()


def _find_null_fields(entry: RawEntry) -> list[str]:
    """
    Find field names whose value is null (YAML's explicit `null` or an
    empty value), regardless of the field's expected type.

    Args:
        entry: A single raw table record.

    Returns:
        Names of fields with a None value.
    """
    return [key for key, value in entry.items() if value is None]


def _find_blank_string_fields(entry: RawEntry) -> list[str]:
    """
    Find field names whose value is a blank or whitespace-only string.

    Args:
        entry: A single raw table record.

    Returns:
        Names of string fields holding an empty or whitespace-only value.
    """
    return [
        key for key, value in entry.items() if _is_blank_string(value)
    ]


def _find_invalid_list_fields(entry: RawEntry) -> list[str]:
    """
    Find field names holding an empty list, or a list containing a None,
    a blank, or whitespace-only string.

    Args:
        entry: A single raw table record.

    Returns:
        Names of list fields that are empty or contain a blank entry.
    """
    blank_fields = []
    for key, value in entry.items():
        if not isinstance(value, list):
            continue
        if not value or any(item is None or _is_blank_string(item) for item in value):
            blank_fields.append(key)
    return blank_fields


def find_invalid_fields(entry: RawEntry) -> list[str]:
    """
    Find all field names with a null, blank, or empty value.

    Combines the null, blank-string, and blank-or-empty-list checks into
    one result, de-duplicated and in first-seen order.

    Args:
        entry: A single raw table record.

    Returns:
        Names of fields with no meaningful value, regardless of type.
    """
    
    return (
        _find_null_fields(entry)
        + _find_blank_string_fields(entry)
        + _find_invalid_list_fields(entry)
    )


def describe_entry(entry: RawEntry, index: int) -> str:
    """
    Build a human-readable identifier for a raw entry, for failure messages.

    Falls back from name, to id, to list position, since either of the
    first two might itself be missing or blank.

    Args:
        entry: A single raw table record.
        index: The entry's position in the source list, used as a last
            resort if neither name nor id is usable.

    Returns:
        A short label identifying the entry.
    """
    name = entry.get("name")
    if isinstance(name, str) and name.strip():
        return f"'{name}'"

    entry_id = entry.get("id")
    if entry_id is not None:
        return f"entry with id {entry_id}"

    return f"entry at list index {index} (no usable name or id)"


def find_duplicate_field_values(table: RawTable, field: str) -> dict[Any, list[int]]:
    """
    Find values in a given field that appear more than once across a table.

    Intended for identity-style fields (e.g. id, name) that are expected
    to be unique across every entry in the table. Entries missing the
    field entirely are skipped — a missing required field is already
    caught by the data quality tests, so this only reports genuine
    duplicate values among entries that actually have one.

    Args:
        table: Raw records for one data table.
        field: The field name to check for cross-entry duplicates.

    Returns:
        A mapping of each duplicated value to the list indices where it occurs.
    """

    seen: dict[Any, list[int]] = {}
    for index, entry in enumerate(table):
        value = entry.get(field)
        if value is None:
            continue
        seen.setdefault(value, []).append(index)

    return {value: indices for value, indices in seen.items() if len(indices) > 1}


def find_duplicate_list_items(entry: RawEntry) -> dict[str, list[Any]]:
    """
    Find list fields where the same non-null item appears more than once
    within that single entry's own list.

    Duplicate values across different entries (e.g. two world tags both
    listing "Pirates" as an enemy) are expected and not checked here.
    Null/None entries are skipped — those are already caught by the data
    quality tests, so this only reports genuine repeated real values.

    Args:
        entry: A single raw table record.

    Returns:
        A mapping of each list field to the duplicated items found in it.
    """
    
    duplicates: dict[str, list[Any]] = {}
    for key, value in entry.items():
        if not isinstance(value, list):
            continue
        real_items = [item for item in value if item is not None]
        seen_items = [item for item in real_items if real_items.count(item) > 1]
        if seen_items:
            duplicates[key] = list(dict.fromkeys(seen_items))

    return duplicates
