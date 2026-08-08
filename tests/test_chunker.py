from src.whisperdesk.core.rag.chunker import chunk_text


def test_short_text_returns_single_chunk():
    text = "This is a short sentence."
    chunks = chunk_text(text, chunk_size=500)
    assert chunks == [text]


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []


def test_long_text_splits_into_multiple_chunks():
    long_text = "Sentence one. " * 100  # well over chunk_size
    chunks = chunk_text(long_text, chunk_size=200, overlap=20)
    assert len(chunks) > 1


def test_chunks_never_exceed_reasonable_size():
    long_text = "Sentence one. " * 100
    chunks = chunk_text(long_text, chunk_size=200, overlap=20)
    # allow some slack for boundary-seeking logic
    assert all(len(c) <= 250 for c in chunks)


def test_no_infinite_loop_on_edge_case():
    # text with no sentence-ending periods at all -- this used to
    # trigger the infinite loop bug we hit and fixed
    text = "word " * 200
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 0