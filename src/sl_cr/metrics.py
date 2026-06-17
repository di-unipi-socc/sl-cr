"""ECLYPSE metric decorators for SL-CR experiments."""

from __future__ import annotations

from eclypse.report.metrics import metric
from eclypse.workflow.event import (
    EventRole,
    every,
)

from .telemetry import RunTelemetry


def get_metrics(telemetry: RunTelemetry) -> list:
    """Build per-run metric events closing over the Prolog telemetry object."""

    @metric.infrastructure()
    def prolog_query_seconds(_, __) -> float:
        return telemetry.last_query_s or float("inf")

    @metric.infrastructure()
    def prolog_inferences(_, __) -> int:
        return telemetry.last_inferences or float("inf")

    @metric.infrastructure()
    def placement_migrations(_, __) -> int:
        return telemetry.last_migrations or float("inf")

    @metric.infrastructure()
    def is_mapped(_, __) -> int:
        return int(bool(telemetry.last_mapping))

    @metric.infrastructure()
    def query_timeout(_, __) -> int:
        return int(bool(telemetry.last_timed_out))

    @every(steps=1, role=EventRole.CALLBACK)
    def telemetry_flush(_):
        telemetry.reset()

    return [
        prolog_query_seconds,
        prolog_inferences,
        placement_migrations,
        is_mapped,
        query_timeout,
        telemetry_flush,
    ]
