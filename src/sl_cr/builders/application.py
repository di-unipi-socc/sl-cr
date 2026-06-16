"""Application builders for ECLYPSE experiment graphs."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random

from eclypse.graph import Application
from eclypse.graph.assets.defaults import (
    availability,
    latency,
    storage,
)

from sl_cr.config import (
    COMPONENT_STORAGE,
    INTERACTION_LATENCY,
)


@dataclass(slots=True)
class AppBuilder:
    """Build ECLYPSE application graphs."""

    components: int
    seed: int | None = None
    add_chain_edges: bool = True

    def build(self) -> Application:
        rng = Random(self.seed)
        application = Application(
            application_id="sl-cr-application",
            node_assets={
                "storage": storage(init_fn_or_value=0),
                "availability": availability(init_fn_or_value=1),
            },
            edge_assets={"latency": latency(init_fn_or_value=0)},
            include_default_assets=False,
        )
        components = [f"c{i}" for i in range(1, self.components + 1)]
        for component in components:
            application.add_node(
                component,
                storage=_randint_range(rng, COMPONENT_STORAGE),
            )

        if self.add_chain_edges:
            for source, target in zip(components, components[1:], strict=False):
                application.add_edge(
                    source,
                    target,
                    strict=False,
                    latency=_randint_range(rng, INTERACTION_LATENCY),
                )
        return application


def _randint_range(rng: Random, value_range: tuple[int, int]) -> int:
    lower, upper = value_range
    return rng.randint(lower, upper)
