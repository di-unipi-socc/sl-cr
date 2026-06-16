"""ECLYPSE metric decorators for SL-CR experiments."""

from __future__ import annotations

from eclypse.report.metrics import metric
from eclypse.placement import Placement

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

    @metric.application()
    def is_mapped(_, placement: Placement, __) -> int:
        return int(bool(placement.mapping))

    @metric.infrastructure()
    def query_timeout(_, __) -> int:
        return int(bool(telemetry.last_timed_out))

    return [
        prolog_query_seconds,
        prolog_inferences,
        placement_migrations,
        is_mapped,
        query_timeout,
    ]
