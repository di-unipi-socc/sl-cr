"""ECLYPSE placement strategy backed by the Prolog CR core."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from eclypse.placement.strategies import PlacementStrategy

from .facts import (
    application_requirements,
    infrastructure_capacities,
)
from .prolog_session import PrologSession

if TYPE_CHECKING:
    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import (
        Placement,
        PlacementView,
    )


class ReasoningMode(StrEnum):
    """Reasoner variants used in the experiments."""

    CR = "cr"
    BASE = "base"


@dataclass(slots=True)
class PLStrategy(PlacementStrategy):
    """Placement strategy whose core decision is delegated to Prolog."""

    mode: ReasoningMode | str = ReasoningMode.CR
    prolog: PrologSession | None = None

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        _: dict[str, Placement],
        __: PlacementView,
    ) -> dict[str, str]:

        if self.prolog is None:
            raise RuntimeError("PLStrategy requires a PrologSession.")

        capacities = infrastructure_capacities(infrastructure)
        requirements = application_requirements(application)
        components = list(application.nodes)

        mapping = self.prolog.solve(
            mode=str(self.mode),
            capacities=capacities,
            requirements=requirements,
            components=components,
        )
        return mapping
