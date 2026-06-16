"""Infrastructure builders for ECLYPSE experiment graphs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import log2
from random import Random

import networkx as nx
from eclypse.graph import Infrastructure
from eclypse.graph.assets.defaults import (
    availability,
    storage,
    latency,
    get_default_path_aggregators,
)

from sl_cr.config import (
    LINK_LATENCY,
    NODE_STORAGE,
)


@dataclass(slots=True)
class InfrBuilder:
    """Build ECLYPSE infrastructure graphs.

    The resulting NetworkX/ECLYPSE graph is the source of truth. Prolog facts are
    generated later from the live graph state, after any ECLYPSE update policy has run.
    """

    nodes: int
    topology: str = "ER"
    seed: int | None = None
    update_policies: Callable | list[Callable] | None = None

    def build(self) -> Infrastructure:
        rng = Random(self.seed)
        graph = self._build_topology()
        node_names = {node: f"n{i}" for i, node in enumerate(graph.nodes, start=1)}
        infrastructure = Infrastructure(
            infrastructure_id="sl-cr-infrastructure",
            node_assets={
                "storage": storage(init_fn_or_value=0),
                "availability": availability(init_fn_or_value=1),
            },
            edge_assets={"latency": latency(init_fn_or_value=0)},
            path_assets_aggregators={
                "latency": get_default_path_aggregators()["latency"]
            },
            include_default_assets=False,
            update_policies=self.update_policies,
        )

        for node in graph.nodes:
            infrastructure.add_node(
                node_names[node],
                strict=False,
                storage=_randint_range(rng, NODE_STORAGE),
            )

        for source, target in graph.to_undirected().edges:
            infrastructure.add_edge(
                node_names[source],
                node_names[target],
                symmetric=True,
                latency=_randint_range(rng, LINK_LATENCY),
            )
        return infrastructure

    def _build_topology(self) -> nx.Graph:
        topology = self.topology.upper()
        if topology == "ER":
            return nx.erdos_renyi_graph(
                self.nodes,
                0.4,
                seed=self.seed,
            )
        if topology == "BA":
            return nx.barabasi_albert_graph(
                self.nodes,
                int(log2(self.nodes)),
                seed=self.seed,
            )
        if topology == "IAG":
            return nx.random_internet_as_graph(
                self.nodes,
                seed=self.seed,
            )
        raise ValueError(f"Unsupported topology {self.topology!r}")


def _randint_range(rng: Random, value_range: tuple[int, int]) -> int:
    lower, upper = value_range
    return rng.randint(lower, upper)
