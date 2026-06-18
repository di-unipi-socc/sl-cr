# SL-CR experiments

Framework for comparing the Prolog continuous-reasoning path against a non-CR recomputation mode.

The files in `input/` are examples of the target Prolog fact shape only. Experiments do not load them. At each ECLYPSE placement, the current `Application` and `Infrastructure` NetworkX graphs are translated into Prolog facts (`node/1`, `caplist/1`, `component/1`, `req_hw/2`), so ECLYPSE update policies that mutate the infrastructure are reflected in the next Prolog query.

The infrastructure update policy is defined in `src/sl_cr/policies.py`. At each simulation step it scales every node's initial storage by a random multiplier sampled from the range configured as `NODE_STORAGE_MULTIPLIER` in `src/sl_cr/config.py`. The current default range is 5--100% of the initial storage.

## Variants

- `cr`: calls the `cr/4` predicate in `src/sl_cr/prolog/main.pl`, using the placement saved by the previous simulation step.
- `base`: disables CR by bypassing `crSep/3`; it calls `repair(P, R, PFixed)` over every component and full capacity budget. This recomputes the whole placement, so no OK frame is preserved.

The first placement of `cr` also uses `repair/3` with a dummy placement, because there is no previous placement to frame yet. Later CR steps use the saved `placement/1` fact.

## Run

```bash
uv run cr
```

Run the smaller debug grid:

```bash
uv run debug
```

Outputs are written by ECLYPSE reporters under Ray Tune trial folders:

- `results/<ray-experiment>/<trial>/output/csv/*.csv`
- `results/<ray-experiment>/<trial>/params.json`

## Metrics

- Prolog query time
- Prolog inferences when available from `statistics(inferences, I)`
- migrations from previous placement
- timeout flag for the latest Prolog placement query
- whether the latest Prolog query produced a valid placement

`notebooks/analyse.ipynb` aggregates these files and plots CR vs non-CR.
