"""
Parametrized tests validating the YAML data tables against their JSON
Schemas, and the TypedDict definitions against those same schemas.
"""

from typing import Any

import jsonschema
import pytest
from pydantic import TypeAdapter

from swn_sector_generator.models.world_tag import WorldTag

TABLE_DEFINITIONS = [
    ("world_tags", "world_tags_schema", WorldTag),
]


def _describe_schema_type(schema_fragment: dict[str, Any]) -> str:
    """
    Describe a JSON Schema type fragment
    in a short, human-readable form.

    Only handles simple, single-type arrays (i.e. list[str]),
    more complex mixed-types (i.e. list[str | int]) won't be properly described.
    Not a concern for our use case due to our data table schema's
    and TypedDict's only being single-type arrays.

    Args:
        schema_fragment: A property's schema dict (e.g. {"type": "array",
            "items": {"type": "string"}}).

    Returns:
        A short description like "string", "integer", or "array of string".
    """
    type_name = schema_fragment.get("type", "unknown")
    if type_name == "array":
        item_type = schema_fragment.get("items", {}).get("type", "unknown")
        return f"array of {item_type}"
    return type_name


@pytest.mark.parametrize(
    "table_fixture, schema_fixture", [(table, schema) for table, schema, _ in TABLE_DEFINITIONS])
def test_table_schema_conforms_to_schema(
        table_fixture: str, schema_fixture: str, request: pytest.FixtureRequest
) -> None:
    """
    Validate that YAML data file conforms to its JSON schemas.

    Args:
        table_fixture: Name of the fixture providing raw table data.
        schema_fixture: Name of the fixture providing the parsed schema.
        request: Pytest's request fixture.
    """

    table = request.getfixturevalue(table_fixture)
    schema = request.getfixturevalue(schema_fixture)

    jsonschema.validate(table, schema)

@pytest.mark.parametrize(
    "typed_dict, schema_fixture",
    [(typed_dict, schema) for _, schema, typed_dict in TABLE_DEFINITIONS]
)
def test_typed_dict_properties_match_schema(
        typed_dict: type, schema_fixture: str, request: pytest.FixtureRequest
) -> None:
    """
    Validate that the TypeDict's properties match to their JSON schema's
    properties.

    Args:
        typed_dict: The TypeDict class to check.
        schema_fixture: Name of the fixture providing the parsed schema.
        request: Pytest's request fixture.
    """

    schema = request.getfixturevalue(schema_fixture)
    schema_properties = set(schema["items"]["properties"].keys())

    generated = TypeAdapter(typed_dict).json_schema()
    generated_properties = set(generated['properties'].keys())

    extra_in_typed_dict = generated_properties - schema_properties
    extra_in_schema = schema_properties - generated_properties

    assert not extra_in_typed_dict and not extra_in_schema, (
        f"{typed_dict.__name__} fields don't match schema properties. "
        f"Extra in {typed_dict.__name__}: {extra_in_typed_dict or 'none'}. "
        f"Extra in schema: {extra_in_schema or 'none'}. "
        f"{typed_dict.__name__} properties should align with schema."
    )


@pytest.mark.parametrize(
    "typed_dict, schema_fixture",
    [(typed_dict, schema) for _, schema, typed_dict in TABLE_DEFINITIONS]
)
def test_typed_dict_required_fields_match_schema(
        typed_dict: type, schema_fixture: str, request: pytest.FixtureRequest
) -> None:
    """
    Validate that the TypeDict's required fields match their JSON schema's
    required fields.

    Args:
        typed_dict: The TypeDict class to check.
        schema_fixture: Name of the fixture providing the parsed schema.
        request: Pytest's request fixture.
    """

    schema = request.getfixturevalue(schema_fixture)
    schema_required = set(schema["items"]["required"])

    generated = TypeAdapter(typed_dict).json_schema()
    generated_required = set(generated.get("required", []))

    extra_in_typed_dict = generated_required - schema_required
    extra_in_schema = schema_required - generated_required

    assert not extra_in_typed_dict and not extra_in_schema, (
        f"{typed_dict.__name__} required fields don't match schema required. "
        f"Extra in {typed_dict.__name__}: {extra_in_typed_dict or 'none'}. "
        f"Extra in schema: {extra_in_schema or 'none'}. "
        f"{typed_dict.__name__} required fields should align with schema."
    )


@pytest.mark.parametrize(
    "typed_dict, schema_fixture",
    [(typed_dict, schema) for _, schema, typed_dict in TABLE_DEFINITIONS],
)
def test_typed_dict_field_types_match_schema(
        typed_dict: type, schema_fixture: str, request:pytest.FixtureRequest
) -> None:
    """
    Validate that the TypeDict's field types match their JSON schema's
    field types.

    Note: mixed-type arrays (list[str | int]) are not reliably checked
    here due to complexity around Pydantic's use of "anyOf". Presently
    not a concern since our tables use only single-type arrays. If
    this ever changes then test will need refactoring.

    Args:
        typed_dict: The TypeDict class to check.
        schema_fixture: Name of the fixture providing the parsed schema.
        request: Pytest's request fixture.
    """

    schema = request.getfixturevalue(schema_fixture)
    schema_properties = schema["items"]["properties"]

    generated = TypeAdapter(typed_dict).json_schema()
    generated_properties = generated["properties"]

    mismatches = []
    for field_name, generated_type in generated_properties.items():
        if field_name not in schema_properties:
            continue # already validating in a separate test
        schema_type = schema_properties[field_name]
        if generated_type.get("type") != schema_type.get("type") or generated_type.get(
            "items", {}
        ).get("type") != schema_type.get("items", {}).get("type"):
            mismatches.append(
                f"{field_name}: TypedDict has {_describe_schema_type(generated_type)}, "
                f"schema has {_describe_schema_type(schema_type)}"", "
                "TypeDict's Python type should match the schema's type. "
                "(i.e. schema 'integer' means field should be declared as int)."
            )

    assert not mismatches, (
        f"{typed_dict.__name__} field types don't match schema: " + "; ".join(mismatches)
    )