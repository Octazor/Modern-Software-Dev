import re


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_tags(text: str) -> list[str]:
    """Extract tags in the form #tag from the text.

    Tags are returned without the leading # and in the order they first appear.
    """

    seen: set[str] = set()
    tags: list[str] = []
    for match in re.finditer(r"#([A-Za-z0-9_]+)", text):
        tag = match.group(1)
        if tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tags
