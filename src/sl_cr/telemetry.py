"""Shared run telemetry reported by ECLYPSE metrics."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RunTelemetry:
    """Mutable placement telemetry owned by one experiment run."""

    mode: str
    last_query_s: float | None = None
    last_inferences: int | None = None
    last_migrations: int = 0
    last_mapping: dict[str, str] = field(default_factory=dict)

    def update(
        self,
        *,
        mapping: dict[str, str],
        query_s: float,
        inferences: int | None,
    ):
        previous = self.last_mapping
        self.last_migrations = sum(
            1
            for component, node in mapping.items()
            if previous.get(component) is not None and previous.get(component) != node
        )
        self.last_mapping = dict(mapping)
        self.last_query_s = query_s
        self.last_inferences = inferences
