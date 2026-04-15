"""Session Manager — Pomodoro cycles, cognitive load tracking, structured reflection.

Manages work sessions with structured timing and cognitive awareness.
Implements the Structured Reflection ouroboros pattern: each Pomodoro cycle
feeds insights from its reflection phase back into the next work block,
creating a self-reinforcing closed loop.

Lifecycle:  INIT → WORK → REFLECT → BREAK/LONG_BREAK → WORK → ...
                                                        ↑           │
                                                        └───────────┘
                                                       (ouroboros loop)
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
    REFLECT = "REFLECT"
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
class ReflectionEntry:
    """A structured reflection captured at the end of a Pomodoro work block.

    The ouroboros pattern: insights from reflection feed forward into the
    next work block, creating a self-reinforcing closed loop.
    """

    reflection_id: str
    pomodoro_number: int
    timestamp: str
    insight: str
    cognitive_load_before: int | None = None
    cognitive_load_after: int | None = None
    carry_forward: str = ""


@dataclass
class Session:
    session_id: str
    phase: SessionPhase = SessionPhase.INIT
    started_at: str = ""
    ended_at: str | None = None
    pomodoro_count: int = 0
    work_blocks: list[WorkBlock] = field(default_factory=list)
    cognitive_loads: list[int] = field(default_factory=list)
    reflections: list[ReflectionEntry] = field(default_factory=list)
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

    @property
    def latest_carry_forward(self) -> str:
        """The most recent reflection's carry_forward — the ouroboros output."""
        if not self.reflections:
            return ""
        return self.reflections[-1].carry_forward

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
            "reflections": [
                {
                    "reflection_id": r.reflection_id,
                    "pomodoro_number": r.pomodoro_number,
                    "timestamp": r.timestamp,
                    "insight": r.insight,
                    "cognitive_load_before": r.cognitive_load_before,
                    "cognitive_load_after": r.cognitive_load_after,
                    "carry_forward": r.carry_forward,
                }
                for r in self.reflections
            ],
            "cognitive_loads": self.cognitive_loads,
            "average_cognitive_load": self.average_cognitive_load,
            "latest_carry_forward": self.latest_carry_forward,
            "pomodoro_minutes": self.pomodoro_minutes,
            "break_minutes": self.break_minutes,
        }


class SessionManager:
    """Manages session lifecycle with Structured Reflection (ouroboros pattern).

    Lifecycle: INIT → WORK → REFLECT → BREAK/LONG_BREAK → WORK → ...
    The REFLECT phase captures insights that carry forward into the next
    work block, creating a self-reinforcing closed loop.
    """

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

        # Transition to REFLECT phase (structured reflection before break)
        session.phase = SessionPhase.REFLECT
        return session

    def reflect(
        self,
        session_id: str,
        insight: str,
        cognitive_load_after: int | None = None,
        carry_forward: str = "",
    ) -> Session:
        """Record a structured reflection — the ouroboros turn.

        The spiral mind processes the completed work block, then outputs an
        insight and a carry_forward item that feeds into the next cycle.
        This creates the self-reinforcing closed loop: each reflection
        strengthens the next Pomodoro.

        Args:
            session_id: The session to reflect on.
            insight: What was learned or observed during the work block.
            cognitive_load_after: Optional post-reflection cognitive load (1-10).
            carry_forward: Actionable item or focus for the next work block.
        """
        session = self._get(session_id)
        if session.phase != SessionPhase.REFLECT:
            raise ValueError(
                f"Cannot reflect: session is in {session.phase.value}. "
                f"Must be in REFLECT (call end_work first)."
            )

        if cognitive_load_after is not None and not (1 <= cognitive_load_after <= 10):
            raise ValueError(f"cognitive_load_after must be 1-10, got {cognitive_load_after}")

        # Get cognitive load from the just-completed work block
        last_block = session.work_blocks[-1] if session.work_blocks else None
        load_before = last_block.cognitive_load if last_block else None

        if cognitive_load_after is not None:
            session.cognitive_loads.append(cognitive_load_after)

        entry = ReflectionEntry(
            reflection_id=str(uuid.uuid4()),
            pomodoro_number=session.pomodoro_count,
            timestamp=datetime.now(timezone.utc).isoformat(),
            insight=insight,
            cognitive_load_before=load_before,
            cognitive_load_after=cognitive_load_after,
            carry_forward=carry_forward,
        )
        session.reflections.append(entry)

        # Complete the ouroboros loop: REFLECT → BREAK or LONG_BREAK
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
