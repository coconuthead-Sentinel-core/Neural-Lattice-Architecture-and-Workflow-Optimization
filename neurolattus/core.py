"""
NeuralLattice — top-level façade that ties zones, workflow engine,
and optimizer together into a single entry point.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from neurolattus.zones import Zone, ZoneType, Task
from neurolattus.workflow import WorkflowEngine, CycleStage, StageHandler
from neurolattus.optimizer import WorkflowOptimizer, OptimizationResult


@dataclass
class NeuralLattice:
    """High-level interface to the Neural Lattice Architecture.

    Usage::

        lattice = NeuralLattice()
        task = lattice.create_task("t1", "Design API schema")
        lattice.run(task)
        result = lattice.optimize()
        print(result.recommendations)
    """

    engine: WorkflowEngine = field(default_factory=WorkflowEngine)
    optimizer: WorkflowOptimizer | None = None

    # Optimizer tunables
    max_green_load: float = 5.0
    max_yellow_load: float = 4.0
    max_red_load: float = 3.0

    def __post_init__(self) -> None:
        if self.optimizer is None:
            self.optimizer = WorkflowOptimizer(
                self.engine,
                max_green_load=self.max_green_load,
                max_yellow_load=self.max_yellow_load,
                max_red_load=self.max_red_load,
            )

    # ------------------------------------------------------------------
    # Task helpers
    # ------------------------------------------------------------------

    def create_task(
        self,
        task_id: str,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> Task:
        task = Task(id=task_id, title=title, description=description, tags=tags or [])
        self.engine.ingest_task(task)
        return task

    # ------------------------------------------------------------------
    # Workflow operations
    # ------------------------------------------------------------------

    def register_handler(self, stage: CycleStage, handler: StageHandler) -> None:
        self.engine.register_handler(stage, handler)

    def run(self, task: Task, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run a task through the full 10-stage execution cycle."""
        return self.engine.run_full_cycle(task, context)

    def step(self, task: Task, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Advance a task by one stage."""
        return self.engine.advance(task, context)

    # ------------------------------------------------------------------
    # Optimization
    # ------------------------------------------------------------------

    def optimize(self) -> OptimizationResult:
        """Analyze the current state and return optimization recommendations."""
        assert self.optimizer is not None
        return self.optimizer.analyze()

    def rebalance(self) -> list[tuple[Task, ZoneType, ZoneType]]:
        """Automatically rebalance tasks across zones to reduce overload."""
        assert self.optimizer is not None
        return self.optimizer.rebalance()

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def cognitive_load(self) -> float:
        return self.engine.total_cognitive_load()

    def summary(self) -> dict[str, Any]:
        """Return a snapshot of the lattice state."""
        result = self.optimize()
        return {
            "cognitive_load": result.cognitive_load,
            "bottleneck": result.bottleneck_zone.value if result.bottleneck_zone else None,
            "recommendations": result.recommendations,
            "metrics": result.metrics,
        }
