import sqlite3
from src.whisperdesk.core.snippets.expander import Snippet


class SnippetRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, trigger: str, expansion: str, case_sensitive: bool = False) -> Snippet:
        self.conn.execute(
            "INSERT OR REPLACE INTO snippets (trigger, expansion, case_sensitive) VALUES (?, ?, ?)",
            (trigger, expansion, int(case_sensitive)),
        )
        self.conn.commit()
        return Snippet(trigger=trigger, expansion=expansion, case_sensitive=case_sensitive)

    def remove(self, trigger: str) -> None:
        self.conn.execute("DELETE FROM snippets WHERE trigger = ?", (trigger,))
        self.conn.commit()

    def get_all(self) -> list[Snippet]:
        rows = self.conn.execute("SELECT * FROM snippets").fetchall()
        return [
            Snippet(
                trigger=row["trigger"],
                expansion=row["expansion"],
                case_sensitive=bool(row["case_sensitive"]),
            )
            for row in rows
        ]