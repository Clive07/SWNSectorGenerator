"""
Address formatting issues with the world tag YAML file

add missing description after the name field for all entries
remove the quotes from all fields in all entries
maintain desired structure
"""

from io import StringIO
from pathlib import Path
# Ensure you've run pip install ruamel.yaml
from ruamel.yaml import YAML


PROJECT_ROOT = Path(__file__).parent.parent
FILE_PATH = PROJECT_ROOT / "src" / "swn_sector_generator" / "resources" / "tables"

INPUT_FILE = FILE_PATH / "world_tags.yaml"
OUTPUT_FILE = FILE_PATH / "world_tags_updated.yaml"


yaml = YAML()

yaml.indent(
    mapping=2,
    sequence=2,
    offset=2,
)

with INPUT_FILE.open("r", encoding="utf-8") as file:
    world_tags = yaml.load(file)

for tag in world_tags:
    if "description" not in tag:
        tag.insert(
            2,
            "description",
            "",
        )

stream = StringIO()

yaml.dump(world_tags, stream)

text = stream.getvalue()

text = text.replace("  - id:", "- id:")

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    file.write(text)