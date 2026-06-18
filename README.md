# Continuous Reasoning Prototype for Application Placement

This repository contains a small declarative Prolog prototype for continuous
reasoning over application placements.

The prototype works on placement states, separates the current placement into
an `OK` fragment and a `KO` fragment, repairs only the `KO` fragment, and
recomposes the repaired placement with the preserved one.

## Requirements

- SWI-Prolog

The implementation uses `library(apply)` for `partition/4`.

## Repository Structure

- `main.pl`: core Prolog prototype.
- `input/`: local input instances.
- `LICENSE`: Apache License 2.0.

## Placement States

A placement state is represented as:

```prolog
s(P, R)
```

where:

- `P` is a list of placement entries `c(Component, Node)`;
- `R` is a list of capacity entries `r(Node, Capacity)`.

For example:

```prolog
s([c(c1,n1), c(c2,n3)], [r(n1,4), r(n2,3), r(n3,1)])
```

represents a state where `c1` is placed on `n1`, `c2` is placed on `n3`, and the
nodes have the listed hardware capacities.

## Problem Facts

An input instance is expected to provide facts such as:

```prolog
component(c1).
component(c2).

node(n1).
node(n2).

req_hw(c1, 2).
req_hw(c2, 2).
```

Deployment policies are expressed through `pi/2`:

```prolog
pi(Component, Node).
```

The default definition in `main.pl` is permissive:

```prolog
pi(_,_) :- true.
```

For constrained instances, replace this clause with a problem-specific
definition, for example one based on allowed node types, latency guards, or
other admissibility predicates.

## Main Predicates

### `crSep/3`

```prolog
crSep(s(P,R), s(Pok,Rok), s(Pko,Rko)).
```

Computes the continuous-reasoning separation of a placement state.

- `Pok` contains the placement entries that can be preserved.
- `Pko` contains the placement entries to repair.
- `Rok` is the resource budget consumed by `Pok`.
- `Rko` is the residual resource budget available for repairing `Pko`.

The separation is induced by `placementOk/2`:

```prolog
placementOk(S, c(C,N)) :- hardwareOk(N, S), pi(C, N).
```

Thus a placement entry is preserved when its node still satisfies the placement
policy and has enough capacity in the current state.

### `repair/3`

```prolog
repair(Pko, Rko, PkoFixed).
```

Repairs only the `KO` placement fragment, using the residual budget `Rko`.
Candidate placements are explored declaratively by Prolog backtracking.

### `cr/4`

```prolog
cr(State, Sok, Sko, Snew).
```

Runs one continuous-reasoning step:

1. separates `State` into `Sok` and `Sko`;
2. repairs the `KO` fragment when needed;
3. recomposes the repaired placement with the preserved one;
4. returns the new placement state `Snew`.

## Minimal Usage

Start SWI-Prolog and consult the prototype together with an input instance:

```prolog
?- [main].
?- [input/my_instance].
```

Then query:

```prolog
?- initial_state(S), cr(S, Sok, Sko, Snew).
```

The expected input predicate `initial_state/1` is not fixed by the prototype:
instances may use any name for their initial state, as long as the queried term
has the form `s(P,R)`.

## Notes

The prototype is intentionally declarative and compact. It is meant to expose
the structure of the continuous-reasoning construction: OK/KO separation,
resource-budget computation, local repair, and recomposition. It does not
implement optimisation criteria, ranking of alternative repairs, or performance
engineering.

