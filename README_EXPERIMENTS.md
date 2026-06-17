# SL-CR experiments

Framework for comparing the Prolog continuous-reasoning path against a non-CR recomputation mode.

The files in `input/` are examples of the target Prolog fact shape only. Experiments do not load them. At each ECLYPSE placement, the current `Application` and `Infrastructure` NetworkX graphs are translated into Prolog facts (`node/1`, `caplist/1`, `component/1`, `req_hw/2`), so ECLYPSE update policies that mutate the infrastructure are reflected in the next Prolog query.

Infrastructure update policies are selected by string in `src/search_space.py` via the `policy` grid key. The policy registry is in `src/policies.py`; it currently supports `none` and `capacity_shock`.

## Variants

- `cr`: calls the Prolog CR predicate. The adapter first checks for `cr/3`, then falls back to the current `cr/4` in `src/sl_cr/prolog/main.pl`.
- `base`: disables CR by bypassing `crSep/3`; it calls `repair(P, R, PFixed)` over every component and full capacity budget. This recomputes the whole placement, so no OK frame is preserved.

The first placement of `cr` also uses `repair/3` with a dummy placement, because there is no previous placement to frame yet. Later CR steps use the saved `placement/1` fact.

## Run

```bash
uv run cr-exp
```

Run one fixed local experiment without Ray Tune:

```bash
uv run debug
```

Outputs are written by ECLYPSE reporters under Ray trial folders:

- `results/<ray-experiment>/<trial>/output/csv/*.csv`
- `results/<ray-experiment>/<trial>/output/simulation_config.json`

## Metrics

- Prolog query time
- Prolog inferences when available from `statistics(inferences, I)`
- migrations from previous placement
- timeout flag for the latest Prolog placement query
- whether the latest Prolog query produced a valid placement
- number of overloaded nodes after placement
- placed components versus total components

`notebooks/01_analyze_results.ipynb` aggregates these files and plots CR vs non-CR.
