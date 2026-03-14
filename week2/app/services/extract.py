from __future__ import annotations

import json
import re
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> list[str]:
    lines = text.splitlines()
    extracted: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


def extract_action_items_llm(text: str) -> list[str]:
    """Use an LLM service to extract action items from *text*.

    Sends a POST request to the local inference endpoint and forces
    a JSON-array response. The returned Python list is obtained by
    parsing the model output; if the response is already a list it is
    returned directly, otherwise we attempt to decode any JSON present
    in the text field.
    """
    url = "http://localhost:11434/api/generate"
    prompt = (
        "Extract action items from the following text and return a JSON array of strings."
        "\nText:\n" + text
    )

    payload: dict[str, Any] = {
        "model": "llama3.2:1b",
        # many llm servers use "input" or "prompt"; we include both
        "input": prompt,
        "prompt": prompt,
        # request strict json formatting
        "format": "json",
    }

    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()

    # the handler may return already-deserialized JSON or a text blob;
    # try to make sense of what we received.
    try:
        data = resp.json()
    except ValueError as exc:  # not valid JSON
        raise ValueError("LLM response was not valid JSON: " + resp.text) from exc

    # common response shapes: the body itself may be the list, or there
    # may be a field such as "output" containing the text.
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # attempt to locate a list anywhere in the dictionary
        for key in ("output", "result", "data", "choices"):
            if key in data:
                value = data[key]
                if isinstance(value, list):
                    return value
                if isinstance(value, str):
                    try:
                        return json.loads(value)
                    except ValueError:
                        pass
        # fall back to attempting to parse the entire dict as text
        text_resp = json.dumps(data)
    else:
        text_resp = str(data)

    # final attempt: parse text for JSON array
    try:
        parsed = json.loads(text_resp)
        if isinstance(parsed, list):
            return parsed
    except ValueError:
        pass

    raise ValueError("Unable to extract JSON array from LLM response: " + resp.text)
