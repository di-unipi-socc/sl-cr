"""ECLYPSE metric decorators for SL-CR experiments."""

from __future__ import annotations

from eclypse.report.metrics import metric

from .telemetry import RunTelemetry


def get_metrics(telemetry: RunTelemetry) -> list:
    """Build per-run metric events closing over the Prolog telemetry object."""

    @metric.infrastructure(name="prolog_query_seconds")
    def prolog_query_seconds(_, __) -> float | None:
        last_query_s = telemetry.last_query_s
        telemetry.last_query_s = None
        return last_query_s

    @metric.infrastructure(name="prolog_inferences")
    def prolog_inferences(_, __) -> int | None:
        last_inferences = telemetry.last_inferences
        telemetry.last_inferences = None
        return last_inferences

    @metric.infrastructure(name="placement_migrations")
    def placement_migrations(_, __) -> int | None:
        last_migrations = telemetry.last_migrations
        telemetry.last_migrations = 0
        return None if last_migrations == 0 else last_migrations

    return [
        prolog_query_seconds,
        prolog_inferences,
        placement_migrations,
    ]
