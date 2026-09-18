# Jet Agents

Jet is a separate Kaggriculture agent family built around a strong public v27
fixed action route.

It keeps the public route as a baseline and tests small, measurable improvements
around it.

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

## 4. Jet 2 — Current Implementation

`src/agents/jet2.py` is a self-contained route agent. Its active macro route is
the same 719-step public V27 route embedded in Jet 1. The current implementation
keeps Jet 1's SELL ranking and adds one selected market intervention: bounded
preemption of an upcoming route sale when both public farms remain sufficiently
similar.

### 4.1 Active runtime pipeline

The action returned on each tick is built by the following pipeline:

```text
719-step route action
        |
        v
hand-count alignment
        |
        v
public-state expert update
        |
        v
WEED repair
        |
        v
terminal liquidation, when applicable
        |
        v
clone-route sale preemption
        |
        v
Jet 1 SELL-slot ranking
        |
        v
final hand-count alignment
```

Each enhancement stage has its own exception boundary. If a stage fails, Jet 2
records the error in its per-seat runtime state and keeps the last valid action.
For the market stage, state changes are prepared on a copy and committed only
after the complete stage succeeds, so a failure cannot leave partially recorded
sale debt.

### 4.2 Selected market behavior

The active market overlay uses only public observations and the agent's own
route:

- a distance is computed from the visible farm assets of both players;
- the clone signal requires 24 consecutive observations with distance at most
  two and cannot latch before tick 160;
- while the signal remains valid, the agent inspects its own sale scheduled two
  ticks later;
- it may advance at most ten units that are already available in its shed;
- every advanced quantity is recorded by product and subtracted from the
  scheduled route sale;
- unpaid quantities are carried forward by at most one tick when the expected
  sale is unavailable;
- the configured market-order limit is respected;
- final liquidation occurs at `episodeSteps - 2` and is based on projected
  same-tick shed contents.

No opponent identity, private opponent inventory, episode identifier, hidden
seed, or future opponent action is used.

### 4.3 Code retained but inactive

The file still contains helpers for opponent-supply estimation, hysteretic
market experts, post-demand sale deferral, contiguous SELL-run ranking, and
sales on otherwise idle market ticks. These helpers are not called by the
active `agent` pipeline and must not be described as active Jet 2 strategy.

The active pipeline deliberately calls `_jet1_rank_sell_slots`; the alternative
run sorter and the general `_market_overlay` remain experimental utilities.

### 4.4 Current limitations

- The agricultural plan is still a fixed route rather than a general planner.
- WEED recovery is local and does not prove that the complete route has been
  resynchronized after a larger divergence.
- Public-farm similarity is only a compact asset-distance heuristic. It does
  not establish that the opponent will sell the same product at the same time.
- Preemption optimizes timing against a route-like opponent and is not evidence
  of universal improvement against unrelated strategies.
- Several market helpers remain in the module despite being inactive, which
  increases review surface and makes the active pipeline less obvious.

## 5. Jet 3 — Ye1 backbone and terminal corrections

`src/agents/jet3.py` is the local baseline for the Jet 4 experiment. It keeps
the complete Ye1 behavior and adds two bounded corrections without replacing
the selected route or its production strategy:

- `_jet3_final_drop` sends carried stock back to the nearest shed just in time
  for the existing terminal liquidation;
- `_jet3_filter_dead_seed_buys` removes seed purchases that the selected
  continuation will never plant;
- the existing observation-based terminal liquidation remains active at
  `episodeSteps - 2`.

On the existing eight-game holdout against Ye1, Jet 3 averaged 85,286.25 final
money versus 84,041.75 for Ye1, a gain of 1,244.50, and won all eight games.

## 6. Jet 4 — Rejected late-hiring experiment

`src/agents/jet4.py` is a self-contained copy of Jet 3 with one additional
filter on `HIRE` market orders. The experiment was motivated by a separate
analysis of 813 top-10 replays: ranks 1–3 averaged about 105 late-game hires per
game, while ranks 8–10 averaged about 119. This correlation was treated only
as an experimental hypothesis: reduce late hiring that may not repay its cost
before the end.

Each `HIRE` order recruits one worker. The public `hires_today` count identifies
the next one-based Fibonacci cost, multiplied by `farmHandCostMult`. Jet 4
assumes a conservative return of one money unit per remaining worker-tick and
keeps a hire only when the ticks remaining through `episodeSteps - 2` are at
least its estimated payback time. Thus the filter is cost- and horizon-based;
it does not disable all hiring after a fixed day. All non-hiring behavior is
unchanged from Jet 3.

The direct benchmark used seeds 0–9, both seats for every seed, and the same
720-step configuration, for 20 paired games:

| Metric | Jet 3 | Jet 4 |
| --- | ---: | ---: |
| Mean final money | 81,960.70 | 80,391.10 |
| Minimum | 54,254.00 | 53,514.00 |
| Maximum | 116,539.00 | 114,292.00 |
| Wins | 20 | 0 |

The paired Jet 4 minus Jet 3 difference averaged -1,569.60, with a minimum of
-3,138.00 and a maximum of -463.00. Neither agent recorded an outer error,
policy error, or fallback. Jet 4 examined 5,580 hire orders, modified 120, and
therefore avoided 120 worker recruitments, or six per game.

Jet 4's record was 0 wins and 20 losses. The experiment is rejected because it
consistently degraded final money. The observed top-10 replay correlation does
not translate into a reproducible gain under this ROI-style payback rule, so
Jet 3 remains the stronger local baseline.

## 7. Jet 5 — Dead fertilizer-purchase filter

`src/agents/jet5.py` starts directly from Jet 3 and does not inherit the
rejected Jet 4 experiment. Its only change tests whether Jet 3 buys fertilizer
that its selected continuation can no longer consume. The hypothesis comes
from the separate 813-replay analysis, in which lower-ranked top-10 teams
bought substantially more fertilizer, especially late in the game; this is a
correlation, not causal evidence.

Fertilizer purchases are represented as
`["BUY_PRODUCT", "FERTILIZER", quantity]`. Each valid `FERTILIZE` actor action
consumes one unit. Before step 72 the filter counts the remaining
`base_backbone` actions through step 71 followed by `known_yarn` from step 72;
from step 72 onward it counts the remaining `known_yarn` continuation. It sums
fertilizer observable in the shed and all carried inventories, conservatively
allows for planned same-tick consumption, and caps purchases at the remaining
planned uses. A purchase is unchanged when fully needed, reduced when partly
excessive, and removed when no additional unit can be consumed. Missing
inventory information leaves the Jet 3 action unchanged, and future fertilizer
collection is deliberately ignored to keep the filter conservative.

The direct benchmark used seeds 0–9, both seats for every seed, and the same
720-step configuration, for 20 paired games:

| Metric | Jet 3 | Jet 5 |
| --- | ---: | ---: |
| Mean final money | 81,798.50 | 81,842.10 |
| Median | 79,470.50 | 79,527.50 |
| Minimum | 54,183.00 | 54,244.00 |
| Maximum | 116,332.00 | 116,379.00 |
| Wins | 2 | 18 |

The paired Jet 5 minus Jet 3 difference averaged +43.60, ranging from -20.00
to +67.00, with no draws. Neither agent recorded an outer error, policy error,
or fallback. Jet 5 examined 360 fertilizer purchases, modified and completely
removed 140 of them, and avoided 400 fertilizer units in total. No partial
reduction occurred in this benchmark, although the filter supports it.

The gain is small but repeated across nine of ten seeds and in both seats.
Jet 5 is therefore retained on this benchmark, while Jet 3 remains the direct
reference baseline for measuring the isolated change.

## 8. Benchmark protocol

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

## 9. Next improvement candidates

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

## 10. Documentation and provenance

Keep the public-route origin explicit in the repository and preserve any
required attribution or license notices from the original public source.

Jet should not be presented as an original CHI strategy. The project's
contribution in this branch is the readable reconstruction, benchmarking and
subsequent runtime/strategy improvements.
