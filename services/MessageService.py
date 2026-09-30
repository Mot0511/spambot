import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "bot.db"


class MessageService:
    """Сервис для управления текстами сообщений для рассылок в SQLite-базе."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Создаёт таблицу, если она не существует."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id   INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL
                )
                """
            )
            conn.commit()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add_message(self, text: str) -> int:
        """Добавляет сообщение, возвращает его id."""
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO messages (text) VALUES (?)",
                (text,),
            )
            conn.commit()
            return int(cur.lastrowid)

    def get_messages(self) -> list[dict]:
        """Возвращает список всех сообщений."""
        with self._connect() as conn:
            rows = conn.execute("SELECT id, text FROM messages").fetchall()
            return [dict(r) for r in rows]

    def get_message(self, message_id: int) -> dict | None:
        """Возвращает сообщение по id либо None."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, text FROM messages WHERE id = ?",
                (message_id,),
            ).fetchone()
            return dict(row) if row else None

    def delete_message(self, message_id: int) -> bool:
        """Удаляет сообщение по id. Возвращает True, если запись удалена."""
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            conn.commit()
            return cur.rowcount > 0
