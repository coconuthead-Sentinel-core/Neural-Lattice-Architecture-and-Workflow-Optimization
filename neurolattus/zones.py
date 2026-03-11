"""
Cognitive zone definitions for the Neural Lattice Architecture.

Zones represent tiers of cognitive load:
  - GREEN: Active work, highest cognitive demand
  - YELLOW: Synthesis and pattern recognition, moderate demand
  - RED: Reference materials and completed work, minimal demand
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class ZoneType(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


# Cognitive load weight per zone (used by the optimizer)
ZONE_WEIGHTS = {
    ZoneType.GREEN: 1.0,
    ZoneType.YELLOW: 0.5,
    ZoneType.RED: 0.1,
}


@dataclass
class Task:
    """A single unit of work that lives in a zone."""

    id: str
    title: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        return self.completed_at is not None

    def complete(self) -> None:
        self.completed_at = datetime.utcnow()


@dataclass
class Zone:
    """A cognitive zone that holds tasks at a given load level."""

    zone_type: ZoneType
    tasks: list[Task] = field(default_factory=list)

    @property
    def weight(self) -> float:
        return ZONE_WEIGHTS[self.zone_type]

    @property
    def cognitive_load(self) -> float:
        """Total cognitive load = number of active tasks * zone weight."""
        active = sum(1 for t in self.tasks if not t.is_complete)
        return active * self.weight

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def active_tasks(self) -> list[Task]:
        return [t for t in self.tasks if not t.is_complete]

    def completed_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.is_complete]
