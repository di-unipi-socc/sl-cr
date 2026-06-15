"""SWI-Prolog MQI adapter used by the ECLYPSE placement strategy."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from swiplserver import (
    PrologResultNotAvailableError,
    PrologThread,
    quote_prolog_identifier,
)

from sl_cr.config import MAIN_PL

from .facts import (
    capacities_to_term,
    mapping_to_placement,
    prolog_atom,
    prolog_term_to_mapping,
)
from .telemetry import RunTelemetry


@dataclass(frozen=True, slots=True)
class PrologResult:
    """Result and metrics for one Prolog placement query."""

    mapping: dict[str, str]
    query: str
    elapsed_s: float
    inferences: int | None
    used_cr: bool


class PrologSession:
    """Use one existing Prolog MQI thread for a whole experiment."""

    def __init__(
        self,
        prolog_thread: PrologThread,
        *,
        telemetry: RunTelemetry,
    ):
        self.thread = prolog_thread
        self.telemetry = telemetry
        self.has_saved_placement = False
        self.saved_mapping: dict[str, str] = {}
        self._consult_main()
        self._declare_dynamic()

    def solve(
        self,
        *,
        mode: str,
        capacities: dict[str, int],
        requirements: dict[str, int],
        components: list[str],
    ) -> PrologResult:
        """Run CR or non-CR placement through the Prolog core."""

        self._reset_assets()
        self._assert_assets(capacities, requirements)

        resources = capacities_to_term(capacities)
        if mode == "non-cr" or not self.has_saved_placement:
            query = self._repair_query(_dummy_placement(components), resources)
            used_cr = False
        elif mode == "cr":
            query = self._cr_query(mapping_to_placement(self.saved_mapping), resources)
            used_cr = True
        else:
            raise ValueError(f"Unsupported reasoning mode {mode!r}")

        before = self._inferences()
        start = perf_counter()
        result = self._query_one(query)
        elapsed = perf_counter() - start
        after = self._inferences()
        mapping = {}
        self.has_saved_placement = False
        if result:
            mapping = prolog_term_to_mapping(result["PFinal"])
            self.save_placement(mapping)

        inferences = None if before is None or after is None else after - before
        self.telemetry.update(mapping=mapping, query_s=elapsed, inferences=inferences)
        return PrologResult(
            mapping=mapping,
            query=query,
            elapsed_s=elapsed,
            inferences=inferences,
            used_cr=used_cr,
        )

    def save_placement(self, mapping: dict[str, str]):
        """Retract and assert the current placement fact for future CR steps."""

        self._query_bool("retractall(placement(_))")
        self._query_bool(f"assert(placement({mapping_to_placement(mapping)}))")
        self.saved_mapping = dict(mapping)
        self.has_saved_placement = True

    def _consult_main(self):
        path = quote_prolog_identifier(str(MAIN_PL))
        self._query_bool(f"consult({path})")

    def _declare_dynamic(self):
        for predicate in (
            "node/1",
            "component/1",
            "req_hw/2",
            "caplist/1",
            "placement/1",
        ):
            self._query_bool(f"dynamic({predicate})")

    def _reset_assets(self):
        for predicate in ("node(_)", "component(_)", "req_hw(_,_)", "caplist(_)"):
            self._query_bool(f"retractall({predicate})")

    def _assert_assets(self, capacities: dict[str, int], requirements: dict[str, int]):
        for node in capacities:
            self._query_bool(f"assert(node({prolog_atom(node)}))")
        for component, requirement in requirements.items():
            component_atom = prolog_atom(component)
            self._query_bool(f"assert(component({component_atom}))")
            self._query_bool(f"assert(req_hw({component_atom},{requirement}))")
        self._query_bool(f"assert(caplist({capacities_to_term(capacities)}))")

    def _cr_query(self, placement: str, resources: str) -> str:
        return f"cr(s({placement},{resources}), _Sok, _Sko, s(PFinal,_RFinal))"

    @staticmethod
    def _repair_query(placement: str, resources: str) -> str:
        return f"repair({placement}, {resources}, PRepaired), sort(PRepaired, PFinal)"

    def _inferences(self) -> int | None:
        try:
            result = self._query_one("statistics(inferences, I)")
            return int(result["I"])
        except Exception:
            return None

    def _query_one(self, query: str) -> dict[str, Any]:
        result = timed_async_query(self.thread, query)
        if result is False:
            # raise RuntimeError(f"Prolog query failed: {query}")
            return None
        if result is True:
            return {}
        if isinstance(result, list):
            if not result:
                raise RuntimeError(f"Prolog query returned no solutions: {query}")
            first = result[0]
            if not isinstance(first, dict):
                raise RuntimeError(f"Unexpected Prolog result: {first!r}")
            return first
        if isinstance(result, dict):
            return result
        raise RuntimeError(f"Unexpected Prolog result: {result!r}")

    def _query_bool(self, query: str) -> bool:
        return bool(timed_async_query(self.thread, query))


def _dummy_placement(components: list[str]) -> str:
    """Create [c(Component, dummy), ...] so repair/3 places every component."""

    return mapping_to_placement({component: "dummy" for component in components})


def timed_async_query(
    prolog: PrologThread,
    query: str,
    timeout: int | None = None,
):
    try:
        prolog.query_async(query, find_all=False)
        r = prolog.query_async_result(wait_timeout_seconds=timeout)
    except PrologResultNotAvailableError:
        print(f"Timeout: {query} took longer than {timeout} seconds.")
        r = None
    finally:
        prolog.cancel_query_async()

    return r
