"""
Type definitions for Stars Without Number world tags.
"""

from typing import TypedDict


class WorldTag(TypedDict):
    """
    Represents a Stars Without Number world tag entry.

    World tags are loaded from the world_tags.yaml resource file and
    describe themes, conflicts, relationships, and points of interest
    associated with a generated world.
    """

    id: int
    name: str
    description: str
    enemies: list[str]
    friends: list[str]
    complications: list[str]
    things: list[str]
    places: list[str]