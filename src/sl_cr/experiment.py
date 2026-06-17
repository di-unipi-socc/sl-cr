"""Experiment orchestration built on a real ECLYPSE Simulation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Mapping,
)

from eclypse.utils._logging import format_log_kv

from eclypse.graph import (
    Application,
    Infrastructure,
)
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)

from .config import TIMEOUT
from .metrics import get_metrics
from .pl_strategy import (
    PLStrategy,
    ReasoningMode,
)
from .prolog_session import PrologSession, _dummy_placement
from .telemetry import RunTelemetry


@dataclass(slots=True)
class Experiment:
    """Run one CR or non-CR ECLYPSE simulation."""

    infrastructure: Infrastructure
    application: Application
    prolog_thread: object
    config: Mapping[str, Any]
    mode: str
    output_path: Path

    def run(self):

        telemetry = RunTelemetry(mode=self.mode)
        prolog = PrologSession(
            self.prolog_thread,
            telemetry=telemetry,
            timeout=int(self.config.get("timeout", TIMEOUT)),
            seed=int(self.config["seed"]),
        )
        sim_config = SimulationConfig(
            seed=int(self.config["seed"]),
            max_steps=int(self.config["steps"]),
            events=get_metrics(telemetry),
            path=self.output_path,
            include_default_metrics=False,
            log_level="CRITICAL",
        )

        sim_config.logger.info(f"Experiment | {format_log_kv(**self.config)}")

        simulation = Simulation(
            infrastructure=self.infrastructure,
            simulation_config=sim_config,
        )
        simulation.register(
            self.application,
            PLStrategy(mode=ReasoningMode(self.mode), prolog=prolog),
        )

        self.output_path.mkdir(parents=True, exist_ok=True)
        # dump_facts(
        #     infrastructure=self.infrastructure,
        #     application=self.application,
        #     output_path=self.output_path,
        #     prolog=prolog,
        # )

        simulation.run()


def dump_facts(
    infrastructure: Infrastructure,
    application: Application,
    output_path: Path,
    prolog: PrologSession,
):
    """Write a Prolog file with facts extracted from the current ECLYPSE state (Infrastructure and Application)."""
    with open(output_path / "kb.pl", "w") as f:
        caplist = "caplist(["

        # NODES
        for node, storage in infrastructure.nodes(data="storage"):
            f.write(f"node({(node)}).\n")
            caplist += f"r({node}, {storage}), "
        caplist = caplist[:-2] + "])."
        f.write("\n")

        # COMPONENTS
        req_hws = []
        for component, req_hw in application.nodes.data("storage"):
            f.write(f"component({(component)}).\n")
            req_hws.append(f"req_hw({component}, {req_hw}).")

        # REQ_HW
        f.write("\n" + "\n".join(req_hws) + "\n")

        # CAP LIST

        # QUERY
        query = prolog._repair_query(
            _dummy_placement(application.nodes()),
            caplist[8:-2],
        )
        f.write("\n" + query + "\n")
    infrastructure.logger.info(f"Dumped facts to {output_path / 'kb.pl'}")
