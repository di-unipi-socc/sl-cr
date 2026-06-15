"""Infrastructure builders for ECLYPSE experiment graphs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from eclypse.graph import Infrastructure
from eclypse.graph.assets.defaults import storage, availability


@dataclass(slots=True)
class InfrBuilder:
    """Build ECLYPSE infrastructure graphs.

    The resulting NetworkX/ECLYPSE graph is the source of truth. Prolog facts are
    generated later from the live graph state, after any ECLYPSE update policy has run.
    """

    topology: str = "path"
    nodes: int = 5
    node_storage: int = 5
    update_policies: Callable | list[Callable] | None = None

    def build(self) -> Infrastructure:
        base_capacities = {f"n{i}": self.node_storage for i in range(1, self.nodes + 1)}
        nodes = list(base_capacities)
        infrastructure = Infrastructure(
            infrastructure_id="sl-cr-infrastructure",
            node_assets={
                "storage": storage(init_fn_or_value=0),
                "availability": availability(init_fn_or_value=1),
            },
            include_default_assets=False,
            update_policies=self.update_policies,
        )

        for node in nodes:
            infrastructure.add_node(
                node,
                strict=False,
                storage=base_capacities[node],
            )
        self._add_edges(infrastructure, nodes)
        return infrastructure

    def _add_edges(self, infrastructure: Infrastructure, nodes: list[str]):
        if self.topology == "none":
            return
        if self.topology == "complete":
            for source in nodes:
                for target in nodes:
                    if source != target:
                        infrastructure.add_edge(source, target, latency=1)
            return
        if self.topology != "path":
            raise ValueError(f"Unsupported topology {self.topology!r}")

        for source, target in zip(nodes, nodes[1:], strict=False):
            infrastructure.add_edge(source, target, symmetric=True, latency=1)
