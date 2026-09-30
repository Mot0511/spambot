import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "bot.db"


class ChannelService:
    """Сервис для управления каналами в SQLite-базе."""

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
                CREATE TABLE IF NOT EXISTS channels (
                    id   INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    link   TEXT UNIQUE NOT NULL
                )
                """
            )
            conn.commit()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add_channel(self, title: str, link: str) -> int:
        """Добавляет канал, возвращает его id."""
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO channels (title, link) VALUES (?, ?)",
                (title, link),
            )
            conn.commit()
            return cur.lastrowid

    def get_channels(self) -> list[dict]:
        """Возвращает список всех каналов."""
        with self._connect() as conn:
            rows = conn.execute("SELECT id, title, link FROM channels").fetchall()
            return [dict(r) for r in rows]

    def get_channel(self, channel_id: int) -> dict | None:
        """Возвращает канал по id либо None."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, title, link FROM channels WHERE id = ?",
                (channel_id,),
            ).fetchone()
            return dict(row) if row else None

    def delete_channel(self, channel_id: int) -> bool:
        """Удаляет канал по id. Возвращает True, если запись удалена."""
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
            conn.commit()
            return cur.rowcount > 0
