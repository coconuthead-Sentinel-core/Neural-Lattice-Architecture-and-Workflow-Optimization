"""Zone Engine — Finite State Machine for GREEN/YELLOW/RED lifecycle.

Implements the zone state machine from Charter Section 3.2 with explicit
transition guards.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from neural_lattice.meta.schemas import (
    ZONE_LOAD_RANGES,
    StatusEnum,
    ZoneEnum,
)


class TransitionError(Exception):
    """Raised when a zone transition violates a guard condition."""


@dataclass
class TransitionResult:
    success: bool
    from_zone: ZoneEnum
    to_zone: ZoneEnum
    timestamp: str
    message: str


# ------------------------------------------------------------------
# Transition guards (Charter Section 3.2)
# ------------------------------------------------------------------


def _guard_green_to_yellow(cognitive_load: int, status: str, **_: Any) -> str | None:
    """Guard: cognitive_load < 7 AND status != DRAFT."""
    if cognitive_load >= 7:
        return f"cognitive_load must be < 7 for GREEN->YELLOW (got {cognitive_load})"
    if status == StatusEnum.DRAFT.value:
        return "Status must not be DRAFT for GREEN->YELLOW"
    return None


def _guard_yellow_to_red(cognitive_load: int, version: str, **_: Any) -> str | None:
    """Guard: cognitive_load < 4 AND version >= 1.0."""
    if cognitive_load >= 4:
        return f"cognitive_load must be < 4 for YELLOW->RED (got {cognitive_load})"
    try:
        if float(version) < 1.0:
            return f"version must be >= 1.0 for YELLOW->RED (got {version})"
    except (ValueError, TypeError):
        return f"Invalid version for YELLOW->RED: {version}"
    return None


def _guard_red_to_yellow(revision_needed: bool = False, **_: Any) -> str | None:
    """Guard: revision_needed must be True."""
    if not revision_needed:
        return "revision_needed must be True for RED->YELLOW reactivation"
    return None


def _guard_red_to_green(scope_change_approved: bool = False, **_: Any) -> str | None:
    """Guard: scope_change_approved must be True."""
    if not scope_change_approved:
        return "scope_change_approved must be True for RED->GREEN major rework"
    return None


# Transition table: (from_zone, to_zone) -> (guard_fn, new_status)
TRANSITIONS: dict[
    tuple[ZoneEnum, ZoneEnum],
    tuple[Any, StatusEnum],
] = {
    (ZoneEnum.GREEN, ZoneEnum.YELLOW): (_guard_green_to_yellow, StatusEnum.ACTIVE),
    (ZoneEnum.YELLOW, ZoneEnum.RED): (_guard_yellow_to_red, StatusEnum.ARCHIVED),
    (ZoneEnum.RED, ZoneEnum.YELLOW): (_guard_red_to_yellow, StatusEnum.ACTIVE),
    (ZoneEnum.RED, ZoneEnum.GREEN): (_guard_red_to_green, StatusEnum.DRAFT),
}


class ZoneEngine:
    """Manages zone lifecycle transitions with guard enforcement."""

    @staticmethod
    def can_transition(
        from_zone: ZoneEnum,
        to_zone: ZoneEnum,
        **context: Any,
    ) -> tuple[bool, str | None]:
        key = (from_zone, to_zone)
        if key not in TRANSITIONS:
            return False, f"No valid transition from {from_zone.value} to {to_zone.value}"

        guard_fn, _ = TRANSITIONS[key]
        error = guard_fn(**context)
        if error:
            return False, error
        return True, None

    @staticmethod
    def transition(
        from_zone: ZoneEnum,
        to_zone: ZoneEnum,
        **context: Any,
    ) -> TransitionResult:
        key = (from_zone, to_zone)
        if key not in TRANSITIONS:
            raise TransitionError(f"No valid transition from {from_zone.value} to {to_zone.value}")

        guard_fn, new_status = TRANSITIONS[key]
        error = guard_fn(**context)
        if error:
            raise TransitionError(error)

        now = datetime.now(timezone.utc).isoformat()
        return TransitionResult(
            success=True,
            from_zone=from_zone,
            to_zone=to_zone,
            timestamp=now,
            message=f"Transitioned {from_zone.value}->{to_zone.value}, status={new_status.value}",
        )

    @staticmethod
    def get_new_status(from_zone: ZoneEnum, to_zone: ZoneEnum) -> StatusEnum:
        key = (from_zone, to_zone)
        if key not in TRANSITIONS:
            raise TransitionError(f"No transition {from_zone.value}->{to_zone.value}")
        _, new_status = TRANSITIONS[key]
        return new_status

    @staticmethod
    def classify_zone(cognitive_load: int) -> ZoneEnum:
        """Classify a zone based on cognitive load value (1-10)."""
        for zone, (lo, hi) in ZONE_LOAD_RANGES.items():
            if lo <= cognitive_load <= hi:
                return zone
        raise ValueError(f"cognitive_load must be 1-10, got {cognitive_load}")
