"""ECLYPSE graph update policies used by experiments."""

from __future__ import annotations

from collections.abc import Callable

from eclypse import policies


def get_policies() -> list[Callable]:
    return [
        policies.failure.kill_nodes(
            0.5,
            revive_probability=0.5,
            revived_availability=1,
        ),
    ]
