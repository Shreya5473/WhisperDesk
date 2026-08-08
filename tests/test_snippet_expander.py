from src.whisperdesk.core.snippets.expander import Snippet, SnippetExpander


def test_expands_matching_trigger():
    expander = SnippetExpander([Snippet(trigger="eml", expansion="test@example.com")])
    result = expander.expand("send it to my eml please")
    assert result == "send it to my test@example.com please"


def test_case_insensitive_by_default():
    expander = SnippetExpander([Snippet(trigger="eml", expansion="test@example.com")])
    result = expander.expand("my EML is here")
    assert "test@example.com" in result


def test_does_not_match_substring_inside_word():
    expander = SnippetExpander([Snippet(trigger="eml", expansion="test@example.com")])
    result = expander.expand("the enamel is shiny")
    assert result == "the enamel is shiny"  # unchanged


def test_no_snippets_returns_text_unchanged():
    expander = SnippetExpander([])
    assert expander.expand("hello world") == "hello world"


def test_empty_text_returns_empty():
    expander = SnippetExpander([Snippet(trigger="eml", expansion="x")])
    assert expander.expand("") == ""