from backend.app.services.extract import extract_tags


def test_extract_tags_simple():
    text = "This is a note with #tag1 and #tag2."
    assert extract_tags(text) == ["tag1", "tag2"]


def test_extract_tags_deduplicates_and_preserves_order():
    text = "#a #b #a #c"
    assert extract_tags(text) == ["a", "b", "c"]


def test_extract_tags_allows_numbers_and_underscores():
    text = "#tag_1 #tag2"
    assert extract_tags(text) == ["tag_1", "tag2"]
