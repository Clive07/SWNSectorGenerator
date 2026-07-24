"""
Tests for the shared validation helper functions in helpers.py.
"""

from helpers import (
    _find_blank_string_fields,
    _find_invalid_list_fields,
    _find_null_fields,
    _is_blank_string,
    describe_entry,
    find_invalid_fields,
    find_duplicate_field_values,
    find_duplicate_list_items,
)


def test_is_blank_string_detects_blank_and_whitespace_only() -> None:
    """
    Empty and whitespace-only strings should be detected as blank.
    """

    assert _is_blank_string("") is True
    assert _is_blank_string("   ") is True


def test_is_blank_string_ignores_non_strings_and_real_content() -> None:
    """
    Non-strings and strings with real content should not be blank.
    """

    assert _is_blank_string(None) is False
    assert _is_blank_string(0) is False
    assert _is_blank_string("Valid") is False


def test_find_null_fields_detects_none() -> None:
    """
    A None value should be detected regardless of the field's expected type.
    """
    
    entry = {"name": "Valid", "description": None, "enemies": None}
    assert _find_null_fields(entry) == ["description", "enemies"]

    
def test_find_blank_string_fields_detects_blank_and_whitespace_only() -> None:
    """
    Blank and whitespace-only string fields should both be detected.
    """

    entry = {"name": "Valid", "description": "   ", "notes": ""}
    assert _find_blank_string_fields(entry) == ["description", "notes"]


def test_find_blank_string_fields_ignores_non_string_values() -> None:
    """
    Non-string values, even falsy ones, should not be reported.
    """

    entry = {"id": 0, "tags": [], "count": None}
    assert _find_blank_string_fields(entry) == []


def test_find_blank_or_empty_list_fields_detects_empty_list() -> None:
    """
    An empty list should be detected as invalid.
    """

    entry = {"name": "Valid", "enemies": []}
    assert _find_invalid_list_fields(entry) == ["enemies"]


def test_find_invalid_or_empty_list_fields_detects_invalid_entries() -> None:
    """
    A list containing a null, blank, or whitespace-only entry should be detected.
    """
    entry = {
        "enemies": ["Pirates", "  "],
        "friends": ["Royal Navy", ""],
        "places": ["Port Royal", None],
    }
    assert _find_invalid_list_fields(entry) == ["enemies", "friends", "places"]


def test_find_blank_or_empty_list_fields_ignores_valid_lists() -> None:
    """
    A list with only meaningful string entries should not be flagged.
    """

    entry = {"enemies": ["Pirates", "Rebels"]}
    assert _find_invalid_list_fields(entry) == []


def test_find_invalid_fields_combines() -> None:
    """
    All three categories of invalid field should be combined.
    """

    entry = {"name": None, "description": "  ", "enemies": [], "friends": [""]}
    assert find_invalid_fields(entry) == ["name", "description", "enemies", "friends"]


def test_describe_entry_prefers_name() -> None:
    """
    A usable name should be preferred over id or index.
    """

    assert describe_entry({"name": "Feral World", "id": 5}, index=0) == "'Feral World'"


def test_describe_entry_falls_back_to_id_when_name_blank() -> None:
    """
    A blank name should fall back to id.
    """

    assert describe_entry({"name": "  ", "id": 5}, index=0) == "entry with id 5"


def test_describe_entry_falls_back_to_index_when_name_and_id_missing() -> None:
    """
    Missing name and id should fall back to list index.
    """

    assert describe_entry({}, index=3) == "entry at list index 3 (no usable name or id)"


def test_find_duplicate_field_values_detects_duplicates() -> None:
    """
    Values appearing more than once in a field should be reported with their indices.
    """

    table = [{"id": 1, "name": "Feral World"}, {"id": 2, "name": "Feral World"}]

    assert find_duplicate_field_values(table, "name") == {"Feral World": [0, 1]}


def test_find_duplicate_field_values_ignores_unique_values() -> None:
    """
    Values appearing only once should not be reported.
    """

    table = [{"id": 1, "name": "Feral World"}, {"id": 2, "name": "Alien Ruins"}]

    assert find_duplicate_field_values(table, "name") == {}


def test_find_duplicate_field_values_ignores_missing_field() -> None:
    """
    Entries missing the field entirely should not be treated as duplicates
    of each other — a missing required field is already caught by the
    data quality tests, so the function only reports real duplicate values.
    """

    table = [{"id": 1}, {"id": 2}]

    assert find_duplicate_field_values(table, "name") == {}


def test_find_duplicate_list_items_detects_repeated_entry() -> None:
    """
    An item repeated within a single entry's own list should be reported.
    """

    entry = {"enemies": ["Pirates", "Pirates", "Rebels"]}

    assert find_duplicate_list_items(entry) == {"enemies": ["Pirates"]}


def test_find_duplicate_list_items_ignores_unique_entries() -> None:
    """
    A list with no repeated items should not be reported.
    """

    entry = {"enemies": ["Pirates", "Rebels"]}

    assert find_duplicate_list_items(entry) == {}


def test_find_duplicate_list_items_ignores_non_list_fields() -> None:
    """
    Non-list fields should be skipped entirely, even if their values repeat.
    """

    entry = {"name": "Feral World", "id": 1, "nickname": "Feral World"}

    assert find_duplicate_list_items(entry) == {}


def test_find_duplicate_list_items_checks_each_list_field_independently() -> None:
    """
    Duplicates should be reported per field, only for fields that actually have them.
    """

    entry = {"enemies": ["Pirates", "Pirates"], "friends": ["Royal Navy", "Pirates"]}

    assert find_duplicate_list_items(entry) == {"enemies": ["Pirates"]}


def test_find_duplicate_list_items_ignores_null_entries() -> None:
    """
    Null entries within a list should not be treated as duplicates of each
    other — that's already caught by the data quality tests, so this function
    only reports repeated real values.
    """
    
    entry = {"enemies": ["Pirates", None, None]}
    assert find_duplicate_list_items(entry) == {}
