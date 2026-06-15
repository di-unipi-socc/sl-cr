"""Search-space definitions for CR experiments."""

from __future__ import annotations

fixed_config = {
    "mode": "cr",
    "steps": 20,
    "nodes": 40,
    "components": 10,
    "node_storage": 8,
    "component_storage": 3,
    "topology": "path",
    "seed": 45,
}


def ray_search_space() -> dict:
    """Build the Ray Tune search space from fixed defaults."""

    from ray import tune

    return {
        "mode": tune.grid_search(["cr", "non-cr"]),
        "steps": 200,
        "nodes": tune.grid_search([25, 50, 100, 200]),
        "components": tune.grid_search([10, 25, 40]),
        "node_storage": tune.grid_search([fixed_config["node_storage"]]),
        "component_storage": tune.grid_search([fixed_config["component_storage"]]),
        "topology": tune.grid_search([fixed_config["topology"]]),
        "seed": tune.grid_search([fixed_config["seed"]]),
    }
