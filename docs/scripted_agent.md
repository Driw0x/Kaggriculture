# Jet — Public-Route Experimental Agents

Jet is a separate Kaggriculture agent family built around a strong public v27
fixed action route.

It is intentionally kept separate from the CHI heuristic-planner lineage.
CHI develops the project's own closed-loop planning logic; Jet keeps the
public route as a baseline and tests small, measurable improvements around it.

## 1. Objective

The Jet branch has two goals:

1. preserve a strong public route as a reproducible competitive baseline;
2. improve robustness around that route without immediately changing the
   macro strategy that makes it strong.

The development rule is therefore:

```text
public route
    |
    v
readable baseline
    |
    v
small isolated change
    |
    v
benchmark
    |
    +---- keep only if it helps
```

## 2. Jet --- readable baseline

`src/agents/jet.py` is the behavior-preserving baseline.

The original route was stored as compressed data. It was mechanically expanded
into a readable Python list containing exactly 719 route actions, organized by
day, hour and step.

The conversion changes representation only. It does not intentionally change
the route actions.

Runtime behavior retained from the public agent includes:

- one fixed action route for the episode;
- hand-count alignment against the current observation;
- actor-local WEED repair around `PLANT` and `BUILD_PASTURE`;
- official-style market-price estimation;
- ordering of route-existing SELL slots by estimated price impact;
- bounded Town-demand weighting in the rebalance regime;
- no opponent identity, episode lookup or future-action lookup.

The baseline remains deliberately route-driven rather than a general planner.

## 3. Jet 1 --- safe fallback and final liquidation

`src/agents/jet1.py` keeps the same 719-step macro route and adds two small
runtime improvements.

### 3.1 Staged runtime fallback

The baseline wraps the complete runtime pipeline in one broad exception
handler. Any unexpected error can therefore replace the entire intended tick
with `PASS`.

Jet 1 isolates the runtime stages:

```text
base route action
      |
      v
WEED repair
      |
      v
final liquidation
      |
      v
SELL ordering
      |
      v
hand alignment
```

If an optional stage fails, the agent keeps the last valid route action. A
complete `PASS` fallback remains only for cases where the base route itself
cannot be recovered.

This is intended as a robustness improvement, not a strategic change.

### 3.2 Observation-based final liquidation

The original route contains fixed final SELL quantities. Jet 1 replaces only
the last actionable market action with liquidation built from the observed
sellable inventory.

The logic:

1. derives the last actionable step from `episodeSteps`;
2. reads current shed contents;
3. projects same-tick `DROP` actions into the shed before market execution;
4. creates one SELL order for each non-empty sellable product;
5. respects the configured maximum number of market orders.

Earlier route actions remain unchanged.

## 4. Relationship with CHI 11

Jet and CHI 11 explore different directions.

| Family | Base strategy | Runtime behavior |
| --- | --- | --- |
| CHI 11 | Project heuristic planner | Closed-loop planning from observations |
| Jet | Public fixed route | Small runtime corrections around the route |

CHI 11 transfers general public ideas into the project's own planner.

Jet directly preserves a public route so improvements can be measured against
a stronger route-based baseline.

The branches should therefore remain separate in code and benchmarks.

## 5. Current versions

| Agent | Status | Main difference |
| --- | --- | --- |
| `jet.py` | Baseline | Readable 719-step route; no intentional route change |
| `jet1.py` | Experimental | Staged fallback + observation-based final liquidation |

No leaderboard improvement should be claimed for Jet 1 until it has been
benchmarked against `jet.py` with identical evaluation conditions.

## 6. Benchmark protocol

Every Jet modification should be compared directly with the previous Jet
version.

Recommended comparison:

```text
same environment configuration
same seeds
both player seats when relevant
jet.py vs jet1.py
```

Record at minimum:

- final money/reward;
- minimum, maximum and mean over repeated games;
- completion/errors;
- final shed inventory;
- final carried inventory;
- number of invalid or lost route actions if instrumented.

A change should remain isolated until its effect is understood.

## 7. Next improvement candidates

The next candidates should preserve the macro route first.

### High priority

1. **Route divergence detection**
   - compare the observed state with checkpoints expected by the route;
   - detect differences in worker positions, inventory, production or money.

2. **WEED resynchronization**
   - replace the fixed replay window with a route-resynchronization condition;
   - resume the route only when the affected actor is back in a compatible
     state.

3. **Local worker remapping**
   - when a worker index no longer matches the expected route state, remap only
     the affected task using current positions;
   - avoid replacing the full route allocator.

4. **Sequential SELL simulation**
   - evaluate multiple SELL orders in their actual execution order;
   - update projected market inventory after each simulated sale.

### Later candidates

- adaptive purchase quantities;
- multiple compatible route checkpoints or route variants;
- opponent-aware supply estimation;
- larger macro-route changes.

These should be attempted only after the baseline and robustness changes are
measured, because the fixed route is currently the main source of Jet's
strength.

## 8. Documentation and provenance

Keep the public-route origin explicit in the repository and preserve any
required attribution or license notices from the original public source.

Jet should not be presented as an original CHI strategy. The project's
contribution in this branch is the readable reconstruction, benchmarking and
subsequent runtime/strategy improvements.
