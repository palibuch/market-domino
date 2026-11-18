"""Append-only, hash-chained research journal for learning-loop experiments.

The journal records claims and outcomes; it does not itself learn, fetch data,
run experiments, trade, or establish that a recorded claim is true. Its hash
chain makes accidental or unsophisticated edits detectable, not impossible.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping
from uuid import uuid4

_GENESIS = "0" * 64
_EVENT_KINDS = frozenset({"hypothesis", "prediction", "outcome", "decision"})


@dataclass(frozen=True)
class JournalEvent:
    sequence: int
    event_id: str
    experiment_id: str
    kind: str
    created_at: str
    payload: dict[str, Any]
    previous_hash: str
    event_hash: str


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("payload must contain finite JSON-compatible values") from error


def _event_digest(
    sequence: int,
    event_id: str,
    experiment_id: str,
    kind: str,
    created_at: str,
    payload_json: str,
    previous_hash: str,
) -> str:
    material = _canonical_json({
        "sequence": sequence,
        "event_id": event_id,
        "experiment_id": experiment_id,
        "kind": kind,
        "created_at": created_at,
        "payload": json.loads(payload_json),
        "previous_hash": previous_hash,
    })
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


class ResearchJournal:
    """Small SQLite event journal with deterministic serialization and hash checks."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS journal_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    experiment_id TEXT NOT NULL,
                    kind TEXT NOT NULL CHECK (kind IN ('hypothesis', 'prediction', 'outcome', 'decision')),
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE
                )"""
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS journal_experiment_idx "
                "ON journal_events(experiment_id, sequence)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10.0)
        connection.row_factory = sqlite3.Row
        return connection

    def append(
        self,
        experiment_id: str,
        kind: str,
        payload: Mapping[str, Any],
        *,
        created_at: datetime | None = None,
    ) -> JournalEvent:
        """Append one immutable event and return its audit metadata."""
        if not isinstance(experiment_id, str) or not experiment_id.strip():
            raise ValueError("experiment_id must be a non-empty string")
        if kind not in _EVENT_KINDS:
            raise ValueError(f"kind must be one of: {', '.join(sorted(_EVENT_KINDS))}")
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be a mapping")
        payload_json = _canonical_json(dict(payload))
        timestamp = created_at or datetime.now(timezone.utc)
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        timestamp_text = timestamp.astimezone(timezone.utc).isoformat()
        event_id = str(uuid4())

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            previous = connection.execute(
                "SELECT sequence, event_hash FROM journal_events ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            sequence = 1 if previous is None else int(previous["sequence"]) + 1
            previous_hash = _GENESIS if previous is None else str(previous["event_hash"])
            digest = _event_digest(
                sequence, event_id, experiment_id, kind, timestamp_text, payload_json, previous_hash
            )
            connection.execute(
                """INSERT INTO journal_events
                   (sequence, event_id, experiment_id, kind, created_at, payload_json,
                    previous_hash, event_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (sequence, event_id, experiment_id, kind, timestamp_text, payload_json,
                 previous_hash, digest),
            )
        return JournalEvent(
            sequence, event_id, experiment_id, kind, timestamp_text,
            json.loads(payload_json), previous_hash, digest,
        )

    def events(self, experiment_id: str | None = None) -> tuple[JournalEvent, ...]:
        """Return events in append order, optionally filtered to one experiment."""
        with self._connect() as connection:
            if experiment_id is None:
                rows = connection.execute(
                    "SELECT * FROM journal_events ORDER BY sequence"
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM journal_events WHERE experiment_id = ? ORDER BY sequence",
                    (experiment_id,),
                ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> JournalEvent:
        return JournalEvent(
            sequence=int(row["sequence"]),
            event_id=str(row["event_id"]),
            experiment_id=str(row["experiment_id"]),
            kind=str(row["kind"]),
            created_at=str(row["created_at"]),
            payload=json.loads(row["payload_json"]),
            previous_hash=str(row["previous_hash"]),
            event_hash=str(row["event_hash"]),
        )

    def verify_chain(self) -> bool:
        """Check sequence continuity, links, and event digests from the genesis."""
        previous_hash = _GENESIS
        expected_sequence = 1
        for event in self.events():
            if event.sequence != expected_sequence or event.previous_hash != previous_hash:
                return False
            try:
                payload_json = _canonical_json(event.payload)
                expected_hash = _event_digest(
                    event.sequence, event.event_id, event.experiment_id, event.kind,
                    event.created_at, payload_json, event.previous_hash,
                )
            except (TypeError, ValueError):
                return False
            if event.event_hash != expected_hash:
                return False
            previous_hash = event.event_hash
            expected_sequence += 1
        return True
