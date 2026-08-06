"""
Tests for the shared validation helper functions in helpers.py.
"""

from helpers import (
    _find_blank_string_fields,
    _find_invalid_list_fields,
    _find_null_fields,
    _is_blank_string,
    _normalise_for_comparison,
    describe_entry,
    find_duplicate_field_values,
    find_duplicate_list_items,
    find_id_range_gaps,
    find_invalid_fields,
    find_untrimmed_string_fields,
)

from swn_sector_generator.loading import RawTable


def test_normalise_for_comparison_casefolds_strings() -> None:
    """
    Strings should be case-folded for comparison.
    """
    assert _normalise_for_comparison("Feral World") == "feral world"
    assert _normalise_for_comparison("FERAL WORLD") == "feral world"
    assert _normalise_for_comparison("feral world") == "feral world"


def test_normalise_for_comparison_leaves_non_strings_unchanged() -> None:
    """
    Non-string values should be returned as-is, since case doesn't apply to them.
    """
    assert _normalise_for_comparison(7) == 7
    assert _normalise_for_comparison(None) is None
    assert _normalise_for_comparison([1, 2]) == [1, 2]


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
    Values appearing more than once in a field should be reported with their original value and index.
    """
    table = [{"id": 1, "name": "Feral World"}, {"id": 2, "name": "Feral World"}]
    assert find_duplicate_field_values(table, "name") == {
        "feral world": [("Feral World", 0), ("Feral World", 1)]
    }


def test_find_duplicate_field_values_detects_case_insensitive_duplicates() -> None:
    """
    Values differing only by case should be treated as duplicates.
    """
    table = [{"id": 1, "name": "Feral World"}, {"id": 2, "name": "feral world"}]
    assert find_duplicate_field_values(table, "name") == {
        "feral world": [("Feral World", 0), ("feral world", 1)]
    }


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
    data quality tests, so this test only reports real duplicate values.
    """
    table = [{"id": 1}, {"id": 2}]
    assert find_duplicate_field_values(table, "name") == {}


def test_find_duplicate_field_values_works_on_non_string_fields() -> None:
    """
    Non-string values (e.g. int ids) should still be compared and detected correctly.
    """
    table = [{"id": 7, "name": "A"}, {"id": 7, "name": "B"}]
    assert find_duplicate_field_values(table, "id") == {7: [(7, 0), (7, 1)]}


def test_find_duplicate_list_items_detects_repeated_entry() -> None:
    """
    An item repeated within a single entry's own list should be reported.
    """
    entry = {"enemies": ["Pirates", "Pirates", "Rebels"]}
    assert find_duplicate_list_items(entry) == {"enemies": ["Pirates"]}


def test_find_duplicate_list_items_detects_case_insensitive_repeats() -> None:
    """
    Items differing only by case should be treated as duplicates.
    """
    entry = {"enemies": ["Pirates", "pirates", "Rebels"]}
    assert find_duplicate_list_items(entry) == {"enemies": ["Pirates", "pirates"]}


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
    other — that's caught by other tests, so this test
    only reports repeated real values.
    """
    entry = {"enemies": ["Pirates", None, None]}
    assert find_duplicate_list_items(entry) == {}


def test_find_untrimmed_string_fields_detects_untrimmed_strings() -> None:
    """
    Untrimmed string fields should be reported as untrimmed strings. whether
    the value is a plain string or a string inside a list, and regardless
    of where in a list the untrimmed item appears.
    """

    entry = {
        "name": " Feral World",
        "nickname": "Alien Ruins ",
        "enemies": ["Pirates "],
        "friends": ["Turncoat Pirate", " Royal Navy"],
    }
    assert find_untrimmed_string_fields(entry) == [
        "name",
        "nickname",
        "enemies",
        "friends",
    ]


def test_find_untrimmed_string_fields_ignores_clean_and_blank_strings() -> None:
    """
    Clean strings, blank/whitespace-only strings, non-string fields, and
    blank list items should not be reported as untrimmed.
    """
    entry = {
        "name": "Feral World",
        "description": "",
        "notes": "   ",
        "id": 1,
        "enemies": ["Pirates", ""],
    }
    assert find_untrimmed_string_fields(entry) == []


def test_find_untrimmed_string_fields_reports_list_field_only_once() -> None:
    """
    A list field with multiple untrimmed items should still only appear
    once in the result, not once per untrimmed item found.
    """
    entry = {"enemies": ["Pirates ", " Rebels", "Scavengers "]}
    assert find_untrimmed_string_fields(entry) == ["enemies"]


def test_find_id_range_gaps_detects_missing_and_unexpected() -> None:
    """
    A mistyped id should surface as one missing value and one unexpected value.
    """
    table = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 6}, {"id": 5}]
    assert find_id_range_gaps(table) == {"missing": [4], "unexpected": [6]}


def test_find_id_range_gaps_ignores_correct_sequence() -> None:
    """
    A table with ids exactly 1..N should report no issues.
    """
    table = [{"id": 1}, {"id": 2}, {"id": 3}]
    assert find_id_range_gaps(table) == {}


def test_find_id_range_gaps_ignores_duplicate_ids() -> None:
    """
    Duplicate ids aren't this function's concern - they're already caught
    by find_duplicate_field_values - so a duplicate shouldn't itself be
    reported as an issue, only whatever id ends up genuinely missing
    because of it.
    """
    table = [{"id": 1}, {"id": 2}, {"id": 2}]
    assert find_id_range_gaps(table) == {"missing": [3]}


def test_find_id_range_gaps_ignores_non_integer_ids() -> None:
    """
    Noninteger id values should be ignored, not counted as valid or invalid.
    """
    table: RawTable = [{"id": 1}, {"id": "two"}, {"id": 3}]
    assert find_id_range_gaps(table) == {"missing": [2]}


def test_find_id_range_gaps_ignores_missing_id_field() -> None:
    """
    An entry with no id field at all should be ignored, not treated as unexpected.
    """
    table = [{"id": 1}, {}, {"id": 3}]
    assert find_id_range_gaps(table) == {"missing": [2]}
