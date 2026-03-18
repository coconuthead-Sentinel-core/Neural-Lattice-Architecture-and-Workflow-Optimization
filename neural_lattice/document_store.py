"""Document Store — SQLite-backed CRUD with zone tracking.

Provides persistent storage for documents with full metadata,
zone assignment, and search capabilities.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

from neural_lattice.meta.schemas import (
    ZoneEnum,
    StatusEnum,
    validate_metadata,
)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id      TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    zone        TEXT NOT NULL CHECK(zone IN ('GREEN','YELLOW','RED')),
    protocol    TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    cognitive_load INTEGER NOT NULL CHECK(cognitive_load BETWEEN 1 AND 10),
    timestamp   TEXT NOT NULL,
    dependencies TEXT NOT NULL DEFAULT '[]',
    tags        TEXT NOT NULL DEFAULT '[]',
    status      TEXT NOT NULL CHECK(status IN ('DRAFT','ACTIVE','TESTING','ARCHIVED','REFERENCE')),
    content     TEXT NOT NULL DEFAULT '',
    version     TEXT NOT NULL DEFAULT '0.1',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
"""

_CREATE_INDEX_ZONE = "CREATE INDEX IF NOT EXISTS idx_documents_zone ON documents(zone);"
_CREATE_INDEX_STATUS = "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);"
_CREATE_INDEX_TAGS = "CREATE INDEX IF NOT EXISTS idx_documents_tags ON documents(tags);"


class DocumentStore:
    """SQLite-backed document storage with zone tracking."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        # For :memory: databases we keep a single persistent connection
        # so the schema survives across calls.
        self._persistent_conn: sqlite3.Connection | None = None
        if self.db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._persistent_conn.row_factory = sqlite3.Row
            self._persistent_conn.execute("PRAGMA foreign_keys=ON")
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(_CREATE_TABLE)
            conn.execute(_CREATE_INDEX_ZONE)
            conn.execute(_CREATE_INDEX_STATUS)
            conn.execute(_CREATE_INDEX_TAGS)

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        if self._persistent_conn is not None:
            # In-memory: reuse the single connection
            try:
                yield self._persistent_conn
                self._persistent_conn.commit()
            except Exception:
                self._persistent_conn.rollback()
                raise
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create(self, meta: dict[str, Any], content: str = "") -> dict[str, Any]:
        """Create a new document. Validates metadata before insertion."""
        errors = validate_metadata(meta)
        if errors:
            raise ValueError(f"Invalid metadata: {'; '.join(errors)}")

        now = datetime.now(timezone.utc).isoformat()
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO documents
                   (doc_id, title, zone, protocol, artifact_type, cognitive_load,
                    timestamp, dependencies, tags, status, content, version,
                    created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    meta["doc_id"],
                    meta["title"],
                    meta["zone"],
                    meta["protocol"],
                    meta["artifact_type"],
                    meta["cognitive_load"],
                    meta["timestamp"],
                    json.dumps(meta["dependencies"]),
                    json.dumps(meta["tags"]),
                    meta["status"],
                    content,
                    meta.get("version", "0.1"),
                    now,
                    now,
                ),
            )
        return self.get(meta["doc_id"])

    def get(self, doc_id: str) -> dict[str, Any] | None:
        """Retrieve a document by ID."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE doc_id = ?", (doc_id,)
            ).fetchone()
        if row is None:
            return None
        return self._row_to_dict(row)

    def update(self, doc_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update fields on an existing document."""
        existing = self.get(doc_id)
        if existing is None:
            raise KeyError(f"Document not found: {doc_id}")

        allowed = {
            "title", "zone", "protocol", "artifact_type", "cognitive_load",
            "timestamp", "dependencies", "tags", "status", "content", "version",
        }
        cols_to_update = {k: v for k, v in updates.items() if k in allowed}
        if not cols_to_update:
            return existing

        # Serialize list fields
        for list_field in ("dependencies", "tags"):
            if list_field in cols_to_update and isinstance(cols_to_update[list_field], list):
                cols_to_update[list_field] = json.dumps(cols_to_update[list_field])

        cols_to_update["updated_at"] = datetime.now(timezone.utc).isoformat()

        set_clause = ", ".join(f"{k} = ?" for k in cols_to_update)
        values = list(cols_to_update.values()) + [doc_id]

        with self._conn() as conn:
            conn.execute(
                f"UPDATE documents SET {set_clause} WHERE doc_id = ?", values
            )
        return self.get(doc_id)  # type: ignore[return-value]

    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID. Returns True if deleted."""
        with self._conn() as conn:
            cursor = conn.execute(
                "DELETE FROM documents WHERE doc_id = ?", (doc_id,)
            )
        return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def list_all(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM documents ORDER BY updated_at DESC"
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def search(
        self,
        zone: str | None = None,
        status: str | None = None,
        tag: str | None = None,
        artifact_type: str | None = None,
        q: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search documents with optional filters."""
        clauses: list[str] = []
        params: list[Any] = []

        if zone:
            clauses.append("zone = ?")
            params.append(zone)
        if status:
            clauses.append("status = ?")
            params.append(status)
        if tag:
            clauses.append("tags LIKE ?")
            params.append(f'%"{tag}"%')
        if artifact_type:
            clauses.append("artifact_type = ?")
            params.append(artifact_type)
        if q:
            clauses.append("(title LIKE ? OR content LIKE ?)")
            params.extend([f"%{q}%", f"%{q}%"])

        where = " AND ".join(clauses) if clauses else "1=1"
        query = f"SELECT * FROM documents WHERE {where} ORDER BY updated_at DESC"

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def count_by_zone(self) -> dict[str, int]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT zone, COUNT(*) as cnt FROM documents GROUP BY zone"
            ).fetchall()
        result = {z.value: 0 for z in ZoneEnum}
        for row in rows:
            result[row["zone"]] = row["cnt"]
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        for list_field in ("dependencies", "tags"):
            if list_field in d and isinstance(d[list_field], str):
                d[list_field] = json.loads(d[list_field])
        return d
