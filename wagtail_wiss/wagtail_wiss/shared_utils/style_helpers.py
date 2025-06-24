import re
from pathlib import Path


def get_class_choices_from_scss(file_path):
    scss_file = Path(file_path)
    if not scss_file.exists():
        return []

    with open(scss_file, "r") as f:
        lines = f.readlines()

    raw_choices = []

    pattern = re.compile(r"\.([\w\-]+)\s*\{(?:\s*//\s*Display Name:\s*(.+))?")

    for line in lines:
        match = pattern.search(line)
        if match:
            class_name = match.group(1)
            display_name = (
                match.group(2).strip()
                if match.group(2)
                else class_name.replace("-", " ").title()
            )
            raw_choices.append((class_name, display_name))

    # Sort alphabetically by display name
    sorted_choices = sorted(raw_choices, key=lambda x: x[1])

    # Ensure "No Style" is first
    return [("", "No Style")] + sorted_choices

