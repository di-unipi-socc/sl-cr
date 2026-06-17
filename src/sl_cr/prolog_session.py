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
from random import shuffle


@dataclass(frozen=True, slots=True)
class TimedQueryResult:
    """Raw MQI result plus timeout status."""

    result: Any
    timed_out: bool


class PrologSession:
    """Use one existing Prolog MQI thread for a whole experiment."""

    def __init__(
        self,
        prolog_thread: PrologThread,
        *,
        telemetry: RunTelemetry,
        timeout: int | None = None,
    ):
        self.thread = prolog_thread
        self.telemetry = telemetry
        self.timeout = timeout
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
    ) -> dict[str, str]:
        """Run CR or non-CR placement through the Prolog core."""

        self.reset_kb()
        self.assert_kb(capacities, requirements)

        resources = capacities_to_term(capacities)
        if mode == "base" or not self.has_saved_placement:
            query = self._repair_query(_dummy_placement(components), resources)
        elif mode == "cr":
            query = self._cr_query(mapping_to_placement(self.saved_mapping), resources)
        else:
            raise ValueError(f"Unsupported reasoning mode {mode!r}")

        before = self._inferences()
        start = perf_counter()
        result, timed_out = self._query_one(query)
        elapsed = perf_counter() - start
        after = self._inferences()
        mapping = {}
        self.has_saved_placement = False
        if result:
            mapping = prolog_term_to_mapping(result["PFinal"])
            self.save_placement(mapping)

        inferences = None if (before is None or after is None) else after - before
        self.telemetry.update(
            mapping=mapping,
            query_s=elapsed,
            inferences=inferences,
            timed_out=timed_out,
        )
        return mapping

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

    def reset_kb(self):
        for predicate in ("node(_)", "component(_)", "req_hw(_,_)", "caplist(_)"):
            self._query_bool(f"retractall({predicate})")

    def assert_kb(self, capacities: dict[str, int], requirements: dict[str, int]):
        nodes = capacities.keys()
        shuffle(list(nodes))
        for node in nodes:
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
            result, _ = self._query_one("statistics(inferences, I)")
            return int(result["I"])
        except Exception:
            return None

    def _query_one(self, query: str) -> tuple[dict[str, Any] | None, bool]:
        result = timed_async_query(self.thread, query, timeout=self.timeout)
        timed_out = result.timed_out
        raw_result = result.result
        if raw_result is None:
            return None, timed_out
        if raw_result is False:
            # raise RuntimeError(f"Prolog query failed: {query}")
            return None, timed_out
        if raw_result is True:
            return {}, timed_out
        if isinstance(raw_result, list):
            if not raw_result:
                raise RuntimeError(f"Prolog query returned no solutions: {query}")
            first = raw_result[0]
            if not isinstance(first, dict):
                raise RuntimeError(f"Unexpected Prolog result: {first!r}")
            return first, timed_out
        if isinstance(raw_result, dict):
            return raw_result, timed_out
        raise RuntimeError(f"Unexpected Prolog result: {raw_result!r}")

    def _query_bool(self, query: str) -> bool:
        return bool(timed_async_query(self.thread, query, timeout=self.timeout).result)


def _dummy_placement(components: list[str]) -> str:
    """Create [c(Component, dummy), ...] so repair/3 places every component."""

    return mapping_to_placement({component: "dummy" for component in components})


def timed_async_query(
    prolog: PrologThread,
    query: str,
    timeout: int | None = None,
) -> TimedQueryResult:
    timed_out = False
    try:
        prolog.query_async(query, find_all=False)
        r = prolog.query_async_result(wait_timeout_seconds=timeout)
    except PrologResultNotAvailableError:
        print(f"Timeout: {query[:10]}... took longer than {timeout} seconds.")
        timed_out = True
        r = None
    finally:
        prolog.cancel_query_async()

    return TimedQueryResult(result=r, timed_out=timed_out)
