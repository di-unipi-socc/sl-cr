"""Shared run telemetry reported by ECLYPSE metrics."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RunTelemetry:
    """Mutable placement telemetry owned by one experiment run."""

    mode: str
    last_query_s: float | None = None
    last_inferences: int | None = None
    last_migrations: int | None = None
    last_timed_out: bool | None = None
    last_mapping: dict[str, str] = field(default_factory=dict)
    previous_mapping: dict[str, str] = field(default_factory=dict)

    def reset(self):
        """Clear values exported by the next metric read."""

        self.last_query_s = None
        self.last_inferences = None
        self.last_migrations = None
        self.last_timed_out = None
        self.last_mapping = {}

    def update(
        self,
        *,
        mapping: dict[str, str],
        query_s: float,
        inferences: int | None,
        timed_out: bool,
    ):
        self.last_migrations = sum(
            1
            for component, node in mapping.items()
            if self.previous_mapping.get(component) is not None
            and self.previous_mapping.get(component) != node
        )
        self.last_mapping = dict(mapping)
        if mapping:
            self.previous_mapping = dict(mapping)
        self.last_query_s = query_s
        self.last_inferences = inferences
        self.last_timed_out = timed_out
