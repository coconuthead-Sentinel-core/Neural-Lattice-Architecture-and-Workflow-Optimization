"""
Workflow engine implementing the Neural Lattice learning and execution cycle.

The cycle consists of 10 stages that map onto the three cognitive zones:

  1. Creative sessions with multiple AI assistants  (GREEN)
  2. Template structuring                           (GREEN)
  3. First-pass reading with highlights              (GREEN)
  4. Confirmation statements                         (YELLOW)
  5. Second-pass review                              (YELLOW)
  6. Handwritten task lists                          (YELLOW)
  7. Photo capture of notes                          (YELLOW)
  8. Template regeneration via AI                    (GREEN)
  9. File storage for persistent reference           (RED)
  10. Periodic printouts for accountability          (RED)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from neurolattus.zones import Zone, ZoneType, Task


class CycleStage(Enum):
    CREATIVE_SESSION = 1
    TEMPLATE_STRUCTURING = 2
    FIRST_PASS_READING = 3
    CONFIRMATION_STATEMENTS = 4
    SECOND_PASS_REVIEW = 5
    HANDWRITTEN_TASK_LISTS = 6
    PHOTO_CAPTURE = 7
    TEMPLATE_REGENERATION = 8
    FILE_STORAGE = 9
    PERIODIC_PRINTOUTS = 10


# Which zone each stage lives in
STAGE_ZONE_MAP: dict[CycleStage, ZoneType] = {
    CycleStage.CREATIVE_SESSION: ZoneType.GREEN,
    CycleStage.TEMPLATE_STRUCTURING: ZoneType.GREEN,
    CycleStage.FIRST_PASS_READING: ZoneType.GREEN,
    CycleStage.CONFIRMATION_STATEMENTS: ZoneType.YELLOW,
    CycleStage.SECOND_PASS_REVIEW: ZoneType.YELLOW,
    CycleStage.HANDWRITTEN_TASK_LISTS: ZoneType.YELLOW,
    CycleStage.PHOTO_CAPTURE: ZoneType.YELLOW,
    CycleStage.TEMPLATE_REGENERATION: ZoneType.GREEN,
    CycleStage.FILE_STORAGE: ZoneType.RED,
    CycleStage.PERIODIC_PRINTOUTS: ZoneType.RED,
}

StageHandler = Callable[[Task, dict[str, Any]], dict[str, Any]]


@dataclass
class WorkflowEngine:
    """Drives tasks through the 10-stage learning and execution cycle."""

    zones: dict[ZoneType, Zone] = field(default_factory=lambda: {
        ZoneType.GREEN: Zone(ZoneType.GREEN),
        ZoneType.YELLOW: Zone(ZoneType.YELLOW),
        ZoneType.RED: Zone(ZoneType.RED),
    })
    stage_handlers: dict[CycleStage, StageHandler] = field(default_factory=dict)
    current_stage: CycleStage = CycleStage.CREATIVE_SESSION

    def register_handler(self, stage: CycleStage, handler: StageHandler) -> None:
        """Register a callback for a specific cycle stage."""
        self.stage_handlers[stage] = handler

    def ingest_task(self, task: Task) -> None:
        """Add a new task to the GREEN zone to start the cycle."""
        self.zones[ZoneType.GREEN].add_task(task)

    def advance(self, task: Task, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Move a task through one stage of the cycle.

        Returns the (possibly updated) context dict produced by the handler.
        """
        ctx = context or {}
        handler = self.stage_handlers.get(self.current_stage)
        if handler is not None:
            ctx = handler(task, ctx)

        target_zone = STAGE_ZONE_MAP[self.current_stage]
        self._migrate_task(task, target_zone)

        # Move to the next stage (wrap around after stage 10)
        next_value = (self.current_stage.value % 10) + 1
        self.current_stage = CycleStage(next_value)

        return ctx

    def run_full_cycle(self, task: Task, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run a task through all 10 stages sequentially."""
        ctx = context or {}
        self.current_stage = CycleStage.CREATIVE_SESSION
        for _ in range(10):
            ctx = self.advance(task, ctx)
        task.complete()
        return ctx

    def total_cognitive_load(self) -> float:
        return sum(z.cognitive_load for z in self.zones.values())

    def _migrate_task(self, task: Task, target: ZoneType) -> None:
        """Ensure a task is in the target zone (move if necessary)."""
        for zt, zone in self.zones.items():
            if zt != target and task in zone.tasks:
                zone.tasks.remove(task)
        if task not in self.zones[target].tasks:
            self.zones[target].add_task(task)
