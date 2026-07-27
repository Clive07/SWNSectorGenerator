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
    return [key for key, value in entry.items() if _is_blank_string(value)]


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


def _normalize_for_comparison(value: Any) -> Any:
    """
    Normalise a value for case-insensitive comparison.

    Strings are case-folded so values differing only by capitalisation
    (e.g. "Feral World" vs "feral world") compare as equal. Non-string
    values are returned unchanged, since case doesn't apply to them.

    Args:
        value: The value to normalise.

    Returns:
        The case-folded string, or the original value if not a string.
    """
    return value.casefold() if isinstance(value, str) else value


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


def find_duplicate_field_values(
    table: RawTable, field: str
) -> dict[Any, list[tuple[Any, int]]]:
    """
    Find values in a given field that appear more than once across a table.

    String values are compared case-insensitively, since a capitalisation-
    only difference (e.g. "Feral World" vs "feral world") almost always
    indicates a typo rather than two intentionally distinct entries.
    Entries missing the field are skipped — already caught elsewhere.

    Args:
        table: Raw records for one data table.
        field: The field name to check for cross-entry duplicates.

    Returns:
        A mapping of each duplicated value to a list of (original value,
        index) pairs where it occurs.
    """
    seen: dict[Any, list[tuple[Any, int]]] = {}
    for index, entry in enumerate(table):
        value = entry.get(field)
        if value is None:
            continue
        seen.setdefault(_normalize_for_comparison(value), []).append((value, index))

    return {key: entries for key, entries in seen.items() if len(entries) > 1}


def find_duplicate_list_items(entry: RawEntry) -> dict[str, list[Any]]:
    """
    Find list fields where the same non-null item appears more than once
    within that single entry's own list.

    Items are compared case-insensitively, since a capitalisation-only
    difference almost always indicates a typo rather than two distinct
    values.

    Duplicate values across different entries (e.g. two world
    tags both listing "Pirates" as an enemy) are not checked here.

    None/Nulls values are also not checked here due to other tests
    checking for this.

    Args:
        entry: A single raw table record.

    Returns:
        A mapping of each list field to the original duplicated items
        found in it.
    """
    duplicates: dict[str, list[Any]] = {}
    for key, value in entry.items():
        if not isinstance(value, list):
            continue
        real_items = [item for item in value if item is not None]

        seen_by_normalized: dict[Any, list[Any]] = {}
        for item in real_items:
            seen_by_normalized.setdefault(_normalize_for_comparison(item), []).append(
                item
            )

        duplicated_originals = [
            original
            for originals in seen_by_normalized.values()
            if len(originals) > 1
            for original in dict.fromkeys(originals)
        ]
        if duplicated_originals:
            duplicates[key] = duplicated_originals
    return duplicates


def find_untrimmed_string_fields(entry: RawEntry) -> list[str]:
    """
    Find fields holding a string with leading or trailing whitespace.

    Checks both plain string fields and strings inside list fields.
    Ignores strings that are blank once stripped, since that's already
    covered by find_invalid_fields.

    Args:
        entry: A single raw table record.

    Returns:
        Names of fields containing an untrimmed string value.
    """

    untrimmed_fields = []
    for key, value in entry.items():
        if isinstance(value, str) and value.strip() and value != value.strip():
            untrimmed_fields.append(key)
        elif isinstance(value, list) and any(
            isinstance(item, str) and item.strip() and item != item.strip()
            for item in value
        ):
            untrimmed_fields.append(key)

    return untrimmed_fields


def find_id_range_gaps(table: RawTable) -> dict[str, list[int]]:
    """
    Find problems with the expected set of ids for this table.

    Assumes ids should collectively cover exactly 1 through the table's
    length, with no gaps and nothing outside that range. This does not
    check whether entries appear in id order within the file - that's a
    separate concern.

    Args:
        table: Raw records for one data table.

    Returns:
        A dict with "missing" (expected ids not found in the table) and
        "unexpected" (ids present that fall outside the expected range),
        each a sorted list. Empty lists are omitted from the result.
    """
    expected_ids = set(range(1, len(table) + 1))
    actual_ids = {
        entry.get("id") for entry in table if isinstance(entry.get("id"), int)
    }

    issues = {}
    if missing := sorted(expected_ids - actual_ids):
        issues["missing"] = missing
    if unexpected := sorted(actual_ids - expected_ids):
        issues["unexpected"] = unexpected
    return issues
