"""Session Manager — Pomodoro cycles, cognitive load tracking, break enforcement.

Manages work sessions with structured timing and cognitive awareness.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SessionPhase(str, Enum):
    INIT = "INIT"
    WORK = "WORK"
    BREAK = "BREAK"
    LONG_BREAK = "LONG_BREAK"
    WRAP_UP = "WRAP_UP"
    CLOSED = "CLOSED"


@dataclass
class WorkBlock:
    block_id: str
    started_at: str
    ended_at: str | None = None
    cognitive_load: int | None = None
    notes: str = ""


@dataclass
class Session:
    session_id: str
    phase: SessionPhase = SessionPhase.INIT
    started_at: str = ""
    ended_at: str | None = None
    pomodoro_count: int = 0
    work_blocks: list[WorkBlock] = field(default_factory=list)
    cognitive_loads: list[int] = field(default_factory=list)
    pomodoro_minutes: int = 25
    break_minutes: int = 5
    long_break_minutes: int = 15
    long_break_interval: int = 4

    @property
    def average_cognitive_load(self) -> float | None:
        if not self.cognitive_loads:
            return None
        return sum(self.cognitive_loads) / len(self.cognitive_loads)

    @property
    def is_break_due(self) -> bool:
        return self.phase == SessionPhase.WORK

    @property
    def is_long_break_due(self) -> bool:
        return self.pomodoro_count > 0 and self.pomodoro_count % self.long_break_interval == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "phase": self.phase.value,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "pomodoro_count": self.pomodoro_count,
            "work_blocks": [
                {
                    "block_id": b.block_id,
                    "started_at": b.started_at,
                    "ended_at": b.ended_at,
                    "cognitive_load": b.cognitive_load,
                    "notes": b.notes,
                }
                for b in self.work_blocks
            ],
            "cognitive_loads": self.cognitive_loads,
            "average_cognitive_load": self.average_cognitive_load,
            "pomodoro_minutes": self.pomodoro_minutes,
            "break_minutes": self.break_minutes,
        }


class SessionManager:
    """Manages session lifecycle: init -> work -> break -> ... -> wrap-up."""

    def __init__(
        self,
        pomodoro_minutes: int = 25,
        break_minutes: int = 5,
        long_break_minutes: int = 15,
        long_break_interval: int = 4,
    ) -> None:
        self.pomodoro_minutes = pomodoro_minutes
        self.break_minutes = break_minutes
        self.long_break_minutes = long_break_minutes
        self.long_break_interval = long_break_interval
        self._sessions: dict[str, Session] = {}

    def init_session(self, session_id: str | None = None) -> Session:
        sid = session_id or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        session = Session(
            session_id=sid,
            phase=SessionPhase.INIT,
            started_at=now,
            pomodoro_minutes=self.pomodoro_minutes,
            break_minutes=self.break_minutes,
            long_break_minutes=self.long_break_minutes,
            long_break_interval=self.long_break_interval,
        )
        self._sessions[sid] = session
        return session

    def start_work(self, session_id: str) -> Session:
        session = self._get(session_id)
        if session.phase not in (SessionPhase.INIT, SessionPhase.BREAK, SessionPhase.LONG_BREAK):
            raise ValueError(
                f"Cannot start work from phase {session.phase.value}. "
                f"Must be in INIT, BREAK, or LONG_BREAK."
            )
        session.phase = SessionPhase.WORK
        block = WorkBlock(
            block_id=str(uuid.uuid4()),
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        session.work_blocks.append(block)
        return session

    def end_work(
        self, session_id: str, cognitive_load: int | None = None, notes: str = ""
    ) -> Session:
        session = self._get(session_id)
        if session.phase != SessionPhase.WORK:
            raise ValueError(f"Cannot end work: session is in {session.phase.value}")

        block = session.work_blocks[-1]
        block.ended_at = datetime.now(timezone.utc).isoformat()
        block.notes = notes
        if cognitive_load is not None:
            if not (1 <= cognitive_load <= 10):
                raise ValueError(f"cognitive_load must be 1-10, got {cognitive_load}")
            block.cognitive_load = cognitive_load
            session.cognitive_loads.append(cognitive_load)

        session.pomodoro_count += 1

        # Determine break type
        if session.is_long_break_due:
            session.phase = SessionPhase.LONG_BREAK
        else:
            session.phase = SessionPhase.BREAK
        return session

    def record_load(self, session_id: str, cognitive_load: int) -> Session:
        """Record a cognitive load measurement mid-session."""
        session = self._get(session_id)
        if not (1 <= cognitive_load <= 10):
            raise ValueError(f"cognitive_load must be 1-10, got {cognitive_load}")
        session.cognitive_loads.append(cognitive_load)
        return session

    def wrap_up(self, session_id: str) -> Session:
        session = self._get(session_id)
        if session.phase == SessionPhase.CLOSED:
            raise ValueError("Session already closed")
        session.phase = SessionPhase.WRAP_UP
        return session

    def close(self, session_id: str) -> Session:
        session = self._get(session_id)
        session.phase = SessionPhase.CLOSED
        session.ended_at = datetime.now(timezone.utc).isoformat()
        return session

    def get_session(self, session_id: str) -> Session:
        return self._get(session_id)

    def list_sessions(self) -> list[Session]:
        return list(self._sessions.values())

    def _get(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Session not found: {session_id}")
        return session
