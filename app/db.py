from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    def init(self) -> None:
        with self._lock:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    vote TEXT NOT NULL,
                    comment TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS escalations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    transcript TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            self._conn.commit()

    def create_session(self) -> str:
        session_id = uuid.uuid4().hex
        now = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO sessions (id, created_at, last_seen_at) VALUES (?, ?, ?)",
                (session_id, now, now),
            )
            self._conn.commit()
        return session_id

    def touch_session(self, session_id: str) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE sessions SET last_seen_at = ? WHERE id = ?",
                (utcnow(), session_id),
            )
            self._conn.commit()

    def ensure_session(self, session_id: str) -> bool:
        row = self._conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return row is not None

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.touch_session(session_id)
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO messages (id, session_id, role, content, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid.uuid4().hex,
                    session_id,
                    role,
                    content,
                    json.dumps(metadata or {}, ensure_ascii=False),
                    utcnow(),
                ),
            )
            self._conn.commit()

    def history(self, session_id: str, limit: int = 100) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]

    def add_feedback(self, session_id: str, vote: str, comment: str | None) -> None:
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO feedback (id, session_id, vote, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uuid.uuid4().hex, session_id, vote, comment, utcnow()),
            )
            self._conn.commit()

    def add_escalation(self, session_id: str, reason: str) -> str:
        ticket_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
        transcript = "\n".join(
            f"{item['role']}: {item['content']}" for item in self.history(session_id, limit=200)
        )
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO escalations (id, session_id, reason, transcript, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (ticket_id, session_id, reason, transcript, utcnow()),
            )
            self._conn.commit()
        return ticket_id
