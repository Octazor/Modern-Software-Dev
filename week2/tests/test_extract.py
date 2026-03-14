import json
from unittest.mock import patch

from ..app.services.extract import extract_action_items


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def _dummy_response(data):
    class DummyResp:
        def __init__(self):
            self._data = data
            self.text = json.dumps(data)

        def raise_for_status(self):
            pass

        def json(self):
            return self._data

    return DummyResp()


@patch("requests.post")
def test_extract_action_items_llm_bullets(mock_post):
    """Normal text with bullet points."""
    mock_post.return_value = _dummy_response(["foo", "bar"])
    from ..app.services.extract import extract_action_items_llm

    result = extract_action_items_llm("- foo\n- bar")
    assert result == ["foo", "bar"]


@patch("requests.post")
def test_extract_action_items_llm_todo_prefix(mock_post):
    """Text with 'TODO:' prefixes."""
    mock_post.return_value = _dummy_response(["do this", "do that"])
    from ..app.services.extract import extract_action_items_llm

    result = extract_action_items_llm("TODO: do this\nTODO: do that")
    assert result == ["do this", "do that"]


@patch("requests.post")
def test_extract_action_items_llm_empty(mock_post):
    """Empty string should still return whatever the model gives."""
    mock_post.return_value = _dummy_response([])
    from ..app.services.extract import extract_action_items_llm

    result = extract_action_items_llm("")
    assert result == []
