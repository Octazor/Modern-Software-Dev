import re
from typing import List


def extract_action_items(text: str) -> List[str]:
    """
    Extract action items from meeting notes text using regex pattern recognition.

    This function identifies potential action items by looking for specific patterns
    commonly used in meeting notes to indicate tasks or follow-ups.

    Args:
        text: The meeting notes text to analyze

    Returns:
        A list of strings representing the extracted action items
    """
    # Define regex patterns for action item detection
    # Patterns are case-insensitive and look for common action item indicators
    patterns = [
        r"^TODO:",  # Lines starting with "TODO:"
        r"^Action:",  # Lines starting with "Action:"
        r"^Follow up:",  # Lines starting with "Follow up:"
        r"We should",  # Lines containing "We should"
        r"Need to",  # Lines containing "Need to"
    ]

    # Compile patterns with case-insensitive flag for better matching
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    # Split text into lines and clean them
    lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]

    results: List[str] = []

    # Check each line against all patterns
    for line in lines:
        for pattern in compiled_patterns:
            if pattern.search(line):
                results.append(line)
                break  # Avoid duplicate entries if multiple patterns match

    return results
