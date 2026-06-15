"""Serialisation helpers for Prolog terms and ECLYPSE graph snapshots.

The files under ``input/`` document the target Prolog shape, but experiments build
facts from live ECLYPSE ``Application`` and ``Infrastructure`` objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from swiplserver import quote_prolog_identifier


@dataclass(frozen=True, slots=True)
class Facts:
    """Infrastructure, application, and placement facts."""

    nodes: list[str]
    capacities: dict[str, int]
    components: list[str]
    requirements: dict[str, int]
    placement: dict[str, str]


def mapping_to_placement(mapping: dict[str, str]) -> str:
    """Return a Prolog placement list term from a Python mapping."""

    items = ",".join(
        f"c({prolog_atom(component)},{prolog_atom(node)})"
        for component, node in mapping.items()
    )
    return f"[{items}]"


def capacities_to_term(capacities: dict[str, int]) -> str:
    """Return a Prolog resource list term from capacity mapping."""

    items = ",".join(
        f"r({prolog_atom(node)},{capacity})" for node, capacity in capacities.items()
    )
    return f"[{items}]"


def infrastructure_capacities(infrastructure) -> dict[str, int]:
    """Translate current ECLYPSE infrastructure nodes into caplist facts."""

    return {
        str(node): int(attrs.get("storage", 0))
        for node, attrs in infrastructure.nodes(data=True)
    }


def application_requirements(application) -> dict[str, int]:
    """Translate current ECLYPSE application services into req_hw facts."""

    return {
        str(component): int(attrs.get("storage", 1))
        for component, attrs in application.nodes(data=True)
    }


def graph_snapshot(infrastructure, application) -> Facts:
    """Return the Prolog-relevant state from live ECLYPSE graphs."""

    capacities = infrastructure_capacities(infrastructure)
    requirements = application_requirements(application)
    return Facts(
        nodes=list(capacities),
        capacities=capacities,
        components=list(requirements),
        requirements=requirements,
        placement={},
    )


def prolog_term_to_mapping(term: Any) -> dict[str, str]:
    """Convert MQI JSON for [c(Component, Node), ...] into a Python mapping."""

    if isinstance(term, str):
        return _parse_placement_string(term)
    if not isinstance(term, list):
        raise ValueError(f"Expected Prolog placement list, got {term!r}")

    mapping: dict[str, str] = {}
    for item in term:
        if isinstance(item, str):
            parsed = _parse_placement_string(item)
            mapping.update(parsed)
            continue
        if not isinstance(item, dict) or item.get("functor") != "c":
            raise ValueError(f"Expected c(Component, Node), got {item!r}")
        component, node = item["args"]
        mapping[str(component)] = str(node)
    return mapping


def _parse_placement_string(value: str) -> dict[str, str]:
    mapping = {}
    for item in value.strip("[]").split("),"):
        if not item:
            continue
        component, node = item.removeprefix("c(").removesuffix(")").split(",", 1)
        mapping[component.strip("' ")] = node.strip("' ")
    return mapping


def prolog_atom(value: str) -> str:
    """Quote a Python string as a Prolog atom."""

    return quote_prolog_identifier(str(value))
