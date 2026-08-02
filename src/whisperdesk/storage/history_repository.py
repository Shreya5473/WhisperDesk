import sqlite3
from dataclasses import dataclass


@dataclass
class Transcription:
    id: int
    text: str
    arabic_text: str | None
    created_at: str
    app_name: str | None
    word_count: int


class HistoryRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, text: str, arabic_text: str | None = None, app_name: str | None = None) -> Transcription:
        word_count = len(text.split())
        cursor = self.conn.execute(
            "INSERT INTO transcriptions (text, arabic_text, app_name, word_count) VALUES (?, ?, ?, ?)",
            (text, arabic_text, app_name, word_count),
        )
        self.conn.commit()
        return self.get_by_id(cursor.lastrowid)

    def get_by_id(self, id: int) -> Transcription | None:
        row = self.conn.execute(
            "SELECT * FROM transcriptions WHERE id = ?", (id,)
        ).fetchone()
        return self._row_to_transcription(row) if row else None

    def get_all(self, limit: int = 100) -> list[Transcription]:
        rows = self.conn.execute(
            "SELECT * FROM transcriptions ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._row_to_transcription(r) for r in rows]

    def search(self, query: str) -> list[Transcription]:
        rows = self.conn.execute(
            "SELECT * FROM transcriptions WHERE text LIKE ? OR arabic_text LIKE ? ORDER BY created_at DESC",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        return [self._row_to_transcription(r) for r in rows]

    def _row_to_transcription(self, row: sqlite3.Row) -> Transcription:
        return Transcription(
            id=row["id"],
            text=row["text"],
            arabic_text=row["arabic_text"],
            created_at=row["created_at"],
            app_name=row["app_name"],
            word_count=row["word_count"],
        )