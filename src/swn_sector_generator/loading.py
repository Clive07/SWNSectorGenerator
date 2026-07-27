"""
Type aliases for raw, unvalidated data read from disk.
"""

from typing import Any


# A YAML table file is always a list of unvalidated record dicts.
RawEntry = dict[str, Any]
RawTable = list[RawEntry]
# A JSON Schema file is always a single dict document.
RawSchema = dict[str, Any]
