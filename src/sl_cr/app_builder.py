"""Application builders for ECLYPSE experiment graphs."""

from __future__ import annotations

from dataclasses import dataclass

from eclypse.graph import Application
from eclypse.graph.assets.defaults import storage, availability


@dataclass(slots=True)
class AppBuilder:
    """Build ECLYPSE application graphs."""

    components: int = 3
    component_storage: int = 2
    add_chain_edges: bool = False

    def build(self) -> Application:
        application = Application(
            application_id="sl-cr-application",
            node_assets={
                "storage": storage(init_fn_or_value=0),
                "availability": availability(init_fn_or_value=1),
            },
            include_default_assets=False,
        )
        components = [f"c{i}" for i in range(1, self.components + 1)]
        for component in components:
            application.add_node(component, storage=self.component_storage)

        if self.add_chain_edges:
            for source, target in zip(components, components[1:], strict=False):
                application.add_edge(source, target, strict=False)
        return application
