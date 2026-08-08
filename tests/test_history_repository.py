import sqlite3
from src.whisperdesk.storage.history_repository import HistoryRepository


def make_test_db():
    conn = sqlite3.connect(":memory:")  # in-memory DB, never touches disk
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            arabic_text TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            app_name TEXT,
            word_count INTEGER
        )
    """)
    return conn


def test_save_and_retrieve():
    repo = HistoryRepository(make_test_db())
    saved = repo.save("hello world", arabic_text="مرحبا")
    assert saved.text == "hello world"
    assert saved.word_count == 2


def test_get_all_returns_saved_entries():
    repo = HistoryRepository(make_test_db())
    repo.save("first entry")
    repo.save("second entry")
    entries = repo.get_all()
    assert len(entries) == 2


def test_search_finds_matching_text():
    repo = HistoryRepository(make_test_db())
    repo.save("meeting notes about the database")
    repo.save("unrelated grocery list")
    results = repo.search("database")
    assert len(results) == 1
    assert "database" in results[0].text