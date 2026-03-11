"""
Workflow optimizer for the Neural Lattice Architecture.

Provides strategies for:
  - Balancing cognitive load across zones
  - Prioritizing tasks to reduce overwhelm
  - Detecting bottlenecks in the execution cycle
  - Recommending zone transitions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from neurolattus.zones import Zone, ZoneType, Task, ZONE_WEIGHTS
from neurolattus.workflow import WorkflowEngine, CycleStage, STAGE_ZONE_MAP


@dataclass
class OptimizationResult:
    """Container for optimizer recommendations."""

    cognitive_load: float
    bottleneck_zone: ZoneType | None
    recommendations: list[str]
    task_priorities: list[tuple[str, float]]  # (task_id, priority_score)
    metrics: dict[str, Any] = field(default_factory=dict)


class WorkflowOptimizer:
    """Analyzes a WorkflowEngine and produces optimization recommendations."""

    def __init__(
        self,
        engine: WorkflowEngine,
        max_green_load: float = 5.0,
        max_yellow_load: float = 4.0,
        max_red_load: float = 3.0,
    ) -> None:
        self.engine = engine
        self.thresholds: dict[ZoneType, float] = {
            ZoneType.GREEN: max_green_load,
            ZoneType.YELLOW: max_yellow_load,
            ZoneType.RED: max_red_load,
        }

    def analyze(self) -> OptimizationResult:
        """Run a full analysis and return recommendations."""
        loads = self._zone_loads()
        bottleneck = self._find_bottleneck(loads)
        recommendations = self._build_recommendations(loads, bottleneck)
        priorities = self._prioritize_tasks()
        metrics = {
            "zone_loads": {zt.value: load for zt, load in loads.items()},
            "total_load": sum(loads.values()),
            "active_tasks": sum(
                len(z.active_tasks()) for z in self.engine.zones.values()
            ),
            "completed_tasks": sum(
                len(z.completed_tasks()) for z in self.engine.zones.values()
            ),
        }

        return OptimizationResult(
            cognitive_load=sum(loads.values()),
            bottleneck_zone=bottleneck,
            recommendations=recommendations,
            task_priorities=priorities,
            metrics=metrics,
        )

    def rebalance(self) -> list[tuple[Task, ZoneType, ZoneType]]:
        """Move tasks between zones to reduce cognitive overload.

        Returns a list of (task, from_zone, to_zone) migrations performed.
        """
        migrations: list[tuple[Task, ZoneType, ZoneType]] = []
        loads = self._zone_loads()

        # Demote excess GREEN tasks to YELLOW
        green = self.engine.zones[ZoneType.GREEN]
        while loads[ZoneType.GREEN] > self.thresholds[ZoneType.GREEN]:
            active = green.active_tasks()
            if not active:
                break
            task = active[-1]  # demote the most recent task
            green.tasks.remove(task)
            self.engine.zones[ZoneType.YELLOW].add_task(task)
            migrations.append((task, ZoneType.GREEN, ZoneType.YELLOW))
            loads = self._zone_loads()

        # Demote excess YELLOW tasks to RED
        yellow = self.engine.zones[ZoneType.YELLOW]
        while loads[ZoneType.YELLOW] > self.thresholds[ZoneType.YELLOW]:
            active = yellow.active_tasks()
            if not active:
                break
            task = active[-1]
            yellow.tasks.remove(task)
            self.engine.zones[ZoneType.RED].add_task(task)
            migrations.append((task, ZoneType.YELLOW, ZoneType.RED))
            loads = self._zone_loads()

        return migrations

    def suggest_next_stage(self) -> CycleStage:
        """Recommend which cycle stage to execute next based on load."""
        loads = self._zone_loads()
        # Prefer stages in the zone with the lightest current load
        lightest_zone = min(loads, key=loads.get)  # type: ignore[arg-type]
        for stage in CycleStage:
            if STAGE_ZONE_MAP[stage] == lightest_zone:
                return stage
        return self.engine.current_stage

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _zone_loads(self) -> dict[ZoneType, float]:
        return {zt: zone.cognitive_load for zt, zone in self.engine.zones.items()}

    def _find_bottleneck(self, loads: dict[ZoneType, float]) -> ZoneType | None:
        for zt, load in loads.items():
            if load > self.thresholds[zt]:
                return zt
        return None

    def _build_recommendations(
        self, loads: dict[ZoneType, float], bottleneck: ZoneType | None
    ) -> list[str]:
        recs: list[str] = []
        if bottleneck is not None:
            recs.append(
                f"Zone {bottleneck.value.upper()} is over capacity "
                f"({loads[bottleneck]:.1f}/{self.thresholds[bottleneck]:.1f}). "
                f"Consider completing or demoting tasks."
            )
        total = sum(loads.values())
        if total == 0:
            recs.append("No active tasks. Ready to ingest new work.")
        elif total < 2.0:
            recs.append("Cognitive load is light. Capacity available for new tasks.")
        elif total > 8.0:
            recs.append(
                "Overall cognitive load is high. "
                "Focus on completing GREEN-zone tasks before adding new work."
            )
        return recs

    def _prioritize_tasks(self) -> list[tuple[str, float]]:
        """Score tasks by urgency: GREEN tasks score highest, older tasks score higher."""
        scored: list[tuple[str, float]] = []
        for zt, zone in self.engine.zones.items():
            for task in zone.active_tasks():
                age_seconds = (
                    __import__("datetime").datetime.utcnow() - task.created_at
                ).total_seconds()
                # Priority = zone weight * (1 + log-scaled age)
                import math
                priority = ZONE_WEIGHTS[zt] * (1 + math.log1p(age_seconds / 3600))
                scored.append((task.id, round(priority, 3)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
