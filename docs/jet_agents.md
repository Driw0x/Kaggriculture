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

The final direct validation used seeds 0–99, both seats for every seed, and the
same 720-step configuration, for 200 paired games. Jet 3 averaged 84,209.90
final money and Jet 5 averaged 84,251.37. The paired Jet 5 minus Jet 3
difference was +41.46. Jet 5 recorded 184 wins and 16 losses, with positive
results on 94 of 100 seeds. Neither agent recorded an outer error, policy
error, or fallback.

The gain is small but reproducible across the larger validation. Jet 5 is the
current retained baseline.

## 8. Jet 6 — Earlier monetization of finished products

### Initial Jet 6 experiment

Jet 6 started from Jet 5 with a late-Tomato viability filter. The hypothesis
came from a correlation in an earlier top-replay analysis, but the selected
Jet 5 continuation emitted no Tomato plant at all. Seeds 0–99, both seats,
therefore produced zero examined or modified Tomato actions, zero avoided
seeds, and a paired mean difference of 0.00. The experiment was inconclusive
and its code was removed.

### Terminal fertilizer correction

A runtime trace then exposed a real terminal defect. At steps 714–717 a worker
could attempt collection on an empty pasture, care for the adjacent animal,
and collect fertilizer only after it was too late to return it to the shed.
Jet 6 now starts that one-tile collection route at step 714, or advances a
step-715 `CARE` to `COLLECT_FERTILIZER`, only when collection, return, and drop
still fit before liquidation. Missing information and unrelated actions are
left unchanged.

The correction scored +1.00 on the 20-game screen. On seeds 0–99 it scored
84,225.79 mean final money versus 84,224.79 for Jet 5: paired mean +0.99,
paired range -21,913 to +21,914, 196 wins and 4 losses, with all 100 seeds
positive after combining their two seats. There were no errors or fallbacks.
Telemetry recorded 400 dead collections examined, 174 recovery routes
started, 373 collections advanced, and 373 fertilizer units recovered. The
rule is retained as a valid bug fix, not as the main Jet 6 improvement.

### Public research and runtime diagnosis

The research phase inspected the following public material:

- the [Lonespear Kaggriculture agent and tuning log](https://github.com/lonespear/kaggriculture),
  whose measured experiments reject late concentrated sales, identify
  endgame inventory leakage, and validate local worker-task clustering;
- the public [Multi-Route Farming Agent](https://www.kaggle.com/code/flexonafft/kaggriculture-multi-route-farming-agent),
  which selects fixed continuations from observable shop state;
- the [COK public agent and strategy notes](https://github.com/COK-ZhangZiliang/Kaggriculture),
  which use fail-closed public-state recovery and projected liquidation;
- the public [AgroBoss notebook](https://www.kaggle.com/code/songoku2005/kaggriculture),
  which uses greedy nearest-worker assignment;
- the [official environment documentation](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md).

The shortlist was deliberately small. Terminal inventory recovery was already
mostly implemented by Jet 5, endgame field filling was already present in the
selected tape, and cluster-based task assignment would replace the fixed
production strategy. Public multi-route selection was directly applicable but
high risk. Earlier product sales were frequent, local, compatible with the
route, and supported by the public finding that a terminal sales concentration
loses value through market impact.

The active continuation was inspected statically and over seeds 0–9, both
seats. Final shed and seed inventories were zero. Before the terminal fix,
16 carried fertilizer units remained across 20 games. The route bought two
land quadrants and did not show evidence that further locked land constrained
production. It emitted 279 `HIRE` orders per game although only the initial
recruitments could succeed; removing those harmless no-ops alone could not
raise final money. The fixed route used only 697 of 7,200 possible market
order slots per game.

Important selected-route market actions were:

| Action and item | Orders | Quantity | First step | Last step | Largest order |
| --- | ---: | ---: | ---: | ---: | ---: |
| `BUY_PRODUCT WHEAT` | 53 | 140 | 1 | 278 | 5 |
| `BUY_PRODUCT FERTILIZER` | 18 | 51 | 150 | 697 | 8 |
| `BUY_SEED WHEAT` | 25 | 187 | 1 | 624 | 11 |
| `BUY_SEED STRAWBERRY` | 15 | 44 | 96 | 264 | 23 |
| `BUY_SEED MELON` | 2 | 13 | 1 | 284 | 12 |
| `BUY_SEED CARROT` | 6 | 10 | 96 | 669 | 3 |
| `BUY_ANIMAL COW` | 5 | 6 | 1 | 176 | 2 |
| `BUY_ANIMAL SHEEP` | 6 | 11 | 1 | 265 | 2 |
| `BUY_LAND` | 2 | 2 | 150 | 265 | 1 |
| `SELL WHEAT` | 57 | 359 | 2 | 718 | 50 |
| `SELL FERTILIZER` | 96 | 358 | 30 | 717 | 17 |
| `SELL WOOL` | 44 | 285 | 150 | 711 | 20 |
| `SELL MILK` | 43 | 236 | 195 | 711 | 15 |
| `SELL STRAWBERRY` | 33 | 272 | 388 | 713 | 16 |
| `SELL MELON` | 8 | 72 | 248 | 264 | 12 |
| `SELL CARROT` | 5 | 18 | 676 | 715 | 6 |

The same 20 runtime games emitted 4,740 `PLANT`, 1,220 `FERTILIZE`,
5,580 `HIRE`, 340 pasture builds, 40 coop builds, and 2,180 placements.
Runtime market totals included 2,800 purchased wheat, 620 purchased
fertilizer after Jet 5's filter, 7,246 sold wheat, 7,244 sold fertilizer,
5,700 sold wool, 4,720 sold milk, 5,440 sold strawberry, 1,440 sold melon,
and 360 sold carrot. Thus production was monetized eventually, but finished
products commonly waited in the shed while market slots went unused. This was
the clearest recurring economic weakness; weak seeds also ended with much less
money, so recovering hundreds per game mattered proportionally more there.

### Candidates tested and retained mechanism

Re-enabling the embedded public multi-route selector was tested first. It
activated on 3,882 recovery-route and 1,246 known-Yarn steps in the 20-game
screen, but reduced mean final money by 3,340.00. It won 7 seeds and lost 3,
with paired results from -32,874 to +15,353. The candidate was rejected and
fully reverted.

The retained mechanism fills otherwise-unused market slots with sales of
finished products already visible in the private shed. It subtracts quantities
already covered by the current action, never exceeds the configured order
limit, and excludes Wheat and Fertilizer because the fixed route can still use
them as inputs. It does not change worker actions, production, purchases, land,
or routing. This is a project-specific transfer of the public sell-timing
finding, not copied public-agent code.

On the seeds 0–9 screen, Jet 6 averaged 81,730.10 versus 80,564.40 for Jet 5.
The paired gain was +1,165.70 (+1.45%), with 18 wins, 2 losses, 9 positive
seeds, 1 negative seed, and no errors. The full seeds 0–99 validation was:

| Metric | Jet 5 | Jet 6 |
| --- | ---: | ---: |
| Mean final money | 83,019.35 | 83,979.63 |
| Median | 82,499.00 | 83,438.00 |
| Minimum | 41,061.00 | 41,934.00 |
| Maximum | 138,151.00 | 138,732.00 |

The paired mean gain was +960.27, or +1.16%, with a paired range of -21,250
to +23,233. Jet 6 recorded 190 wins, 10 losses, and no draws. At seed level,
96 were positive, 4 negative, and none neutral. The large paired extremes were
opposite-seat interaction effects; their seed totals remained representative,
and the gain was not dependent on a few outliers. There were no outer errors,
policy errors, or fallbacks. Early-sale telemetry recorded 7,028 opportunities,
6,469 added orders, 42,101 offered units, and 3,001 opportunities observed on
turns whose market order list was already full.

The untouched holdout used seeds 100–129, both seats. Jet 5 averaged 80,703.08
and Jet 6 averaged 81,842.42. The paired gain was +1,139.33, or +1.41%, with
a range of -219 to +3,009. Jet 6 recorded 59 wins, 1 loss, and no draws; all
30 seeds were positive. There were no errors or fallbacks. Holdout telemetry
recorded 2,104 opportunities, 1,936 added orders, 12,723 offered units, and
900 full-market skips. No threshold was tuned on the holdout.

The early-sale mechanism is therefore retained. Together with the terminal
fertilizer bug fix, it makes Jet 6 the new local baseline. This conclusion is
limited to the paired local benchmarks and is not a leaderboard claim.

## 9. Benchmark protocol

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

## 10. Next improvement candidates

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

## 11. Documentation and provenance

Keep the public-route origin explicit in the repository and preserve any
required attribution or license notices from the original public source.

Jet should not be presented as an original CHI strategy. The project's
contribution in this branch is the readable reconstruction, benchmarking and
subsequent runtime/strategy improvements.
