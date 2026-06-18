"""ECLYPSE graph update policies used by experiments."""

from __future__ import annotations

from collections.abc import Callable

from sl_cr.config import NODE_STORAGE_MULTIPLIER


def get_policies() -> list[Callable]:
    return [scale_initial_storage()]


def scale_initial_storage(
    multiplier_range: tuple[float, float] = NODE_STORAGE_MULTIPLIER,
    *,
    storage_key: str = "storage",
) -> Callable:
    """Scale each node's initial storage by a random multiplier at every step."""

    lower, upper = multiplier_range
    if lower < 0 or upper < 0 or lower > upper:
        raise ValueError(f"Invalid storage multiplier range: {multiplier_range!r}")

    initial_storage: dict[str, float] = {}

    def policy(graph):
        for node, data in graph.nodes(data=True):
            initial = initial_storage.setdefault(
                str(node),
                float(data.get(storage_key, 0)),
            )
            multiplier = graph.rnd.uniform(lower, upper)
            data[storage_key] = round(initial * multiplier, 6)

        graph.logger.trace("Applied scale_initial_storage policy.")

    return policy
