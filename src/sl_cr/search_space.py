"""Search-space definitions for CR experiments."""

from __future__ import annotations

from ray import tune

from sl_cr.config import (
    STEPS,
    TIMEOUT,
)

fixed_config = {
    "mode": "cr",
    "steps": 10,
    "nodes": 1024,
    "components": 300,
    "topology": "IAG",
    "seed": 3997,
    "timeout": TIMEOUT,
}


def complete_search_space() -> dict:

    return {
        "steps": STEPS,
        "timeout": TIMEOUT,
        "mode": tune.grid_search(["cr", "base"]),
        "nodes": tune.grid_search([250, 500, 750, 1000]),
        "components": tune.grid_search([50, 100, 200, 300]),
        "topology": tune.grid_search(["ER", "BA", "IAG"]),
        "seed": tune.grid_search([3997, 151195, 300425, 180192, 481183]),
    }


def debug_search_space() -> dict:

    return {
        "mode": tune.grid_search(["cr", "base"]),
        "timeout": TIMEOUT,
        "steps": 10,
        "nodes": 1500,
        "components": 100,
        "topology": "ER",
        "seed": 3997,
    }
