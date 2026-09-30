# Public Agents

This document groups only the Kaggriculture agents that belong to the public-derived
or public-reference line retained in the repository.

The numbering below is the documentation numbering used by this file. Original
source filenames are preserved for provenance and reproducibility.

## Alias mapping

| Public Agent | Original name | Original artifact | Role |
| --- | --- | --- | --- |
| Public Agent 1 | CHI11 | `src/agents/chi11.py` | CHI10 + public-meta overlay |
| Public Agent 2 | Ye | `src/agents/ye.py` | Retained public V58 reference |
| Public Agent 3 | Ye1 | `src/agents/ye1.py` | Hardened V58 execution |
| Public Agent 4 | Jet | `src/agents/jet.py` | Readable public V27 route baseline |
| Public Agent 5 | Jet1 | `src/agents/jet1.py` | Fallback isolation + terminal liquidation |
| Public Agent 6 | Jet2 | `src/agents/jet2.py` | Public-state sale preemption overlay |
| Public Agent 7 | Jet3 | `src/agents/jet3.py` | Public Agent 3 backbone + terminal corrections |
| Public Agent 8 | Jet4 | `src/agents/jet4.py` | Rejected late-hiring experiment |
| Public Agent 9 | Jet5 | `src/agents/jet5.py` | Dead fertilizer-purchase filter |
| Public Agent 10 | Jet6 | `src/agents/jet6.py` | Earlier monetization + terminal fertilizer correction |

## Lineage

These versions do not form one single inheritance chain.

```text
CHI10
└── Public Agent 1

Public Agent 2
└── Public Agent 3

Public Agent 4
├── Public Agent 5
│   └── Public Agent 6
└── Public Agent 7  (built from Public Agent 3 behavior)
    ├── Public Agent 8  (rejected experiment)
    └── Public Agent 9
        └── Public Agent 10
```

The lineage follows the relationships explicitly documented in the supplied
agent notes; numbering is only a unified documentation convention.

## Public Agent 1 — Public-meta shop and market overlay

**Original name:** CHI11  
**Source:** `src/agents/chi11.py`

`src/agents/chi11.py` is an experimental CHI 10 variant informed by public
high-scoring Kaggriculture work. It deliberately transfers general mechanisms
instead of copying replay action tapes.

Public Agent 1 keeps the CHI 10 economic planner and adds a small observation-only
overlay based on public game state.

### Public Agent 1.1 Public references

- Kaito Fukami's public v48 notebook (historical public score 3009.0):
  https://www.kaggle.com/code/kaitofukami/40-40-early-floor-39-46-top-10-v48-fast-routes
- GzmCR's scenario-aware economic policy:
  https://github.com/GzmCR/Kaggriculture
- lonespear's replay, market and routing analysis:
  https://github.com/lonespear/kaggriculture

Kaito's v48 routes on the order of publicly visible shop unlocks, selects only
one child controller per turn, and gives collision-sensitive sales explicit
priority. Public Agent 1 adapts those ideas to CHI 10's closed-loop planner.

### Public Agent 1.2 Changes from CHI 10

The retained changes are:

1. the first and second unlocked shops apply small 8% and 3% demand priors to
   otherwise unchanged marginal production scores;
2. a public farm signature tracks whether both farms remain nearly identical
   for 24 consecutive turns;
3. existing `SELL` slots are reordered by estimated price impact while every
   non-sale order keeps its original slot;
4. during a sustained clone state, ordinary sale batches are capped at ten to
   reduce simultaneous market collision;
5. CHI 10 is called exactly once per observation.

No opponent identity, rating, episode ID, hidden inventory, replay lookup or
future action is used. Final-day liquidation is never capped.

### Public Agent 1.3 Shop-order production prior

The order of unlocked shops is used as a mild production prior.

The first unlocked shop applies an 8% multiplier and the second a 3%
multiplier to production whose output matches the corresponding public shop
demand.

These multipliers are applied on top of the existing CHI 10 production score:

```text
Public Agent 1 score = CHI 10 score × public shop multiplier
```

The adjustment remains deliberately small so the existing marginal-profit
calculation stays decisive unless candidate productions are already close.

### Public Agent 1.4 Public farm-similarity detection

Public Agent 1 builds a compact signature from information already visible in the
observation:

- crop counts;
- animal counts;
- number of unlocked quadrants;
- number of farm hands.

The two farms are considered persistently similar only after repeated
near-equality of these public signatures.

The retained thresholds are:

```text
detection starts at step 48
signature distance <= 2
24 consecutive matching turns
overlay can become active from step 160
```

### Public Agent 1.5 Market-impact-aware SELL ordering

Public Agent 1 does not create a separate sale strategy. It only reorders SELL orders
that already exist in the CHI 10 action.

For every existing sale, the planner estimates the immediate price impact from
the quantity being sold:

```text
impact = quantity × max(current price - post-sale price, 0)
```

SELL slots with the largest estimated impact are executed first, while every
non-SELL market slot keeps its original position.

During a sustained public clone state, ordinary sale quantities are capped at
10 units to reduce simultaneous market collision. Final-day liquidation is
never capped.

### Public Agent 1.6 Standalone submission

Public Agent 1 embeds the CHI 10 implementation directly in the same module.

The final `agent(obs)`:

1. detects the public-meta state;
2. temporarily applies the shop-order production multiplier;
3. calls the embedded CHI 10 agent exactly once;
4. restores the original production scoring function;
5. reorders the resulting SELL slots.

No project-local import is required, so `chi11.py` can be submitted directly
as a single Kaggle agent file.

### Public Agent 1.7 Relationship with Public Agent 4

Public Agent 4 is a separate experimental branch and is not a Public Agent 1 successor.

Public Agent 1 transfers selected public ideas into the project's own closed-loop
heuristic planner. Public Agent 4 instead keeps a strong public fixed action route as its
baseline so the route can be inspected and improved directly.

Keeping the two families separate makes CHI improvements and route-derived
improvements independently measurable.

### Public Agent 1.8 Preliminary local validation

The deterministic comparison uses seeds 1101 and 1102 in both seats:

| Seed | Public Agent 1 seat | Public Agent 1 | CHI 10 | Margin |
| ---: | ---: | ---: | ---: | ---: |
| 1101 | 0 | 102,843 | 91,104 | +11,739 |
| 1101 | 1 | 104,727 | 100,928 | +3,799 |
| 1102 | 0 | 82,811 | 82,009 | +802 |
| 1102 | 1 | 84,203 | 79,258 | +4,945 |

Result: 4/4 wins, mean margin +5,321.2. This is a small development screen,
not evidence of leaderboard improvement.

Run the comparison with:

```powershell
.\.venv\Scripts\python.exe experiments\compare_chi11.py
```

Focused unit tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_chi11.py -q -p no:cacheprovider
```

## Public Agent 2 — Retained public V58 agent

**Original name:** Ye  
**Source:** `src/agents/ye.py`

`src/agents/ye.py` is the retained standalone V58 public agent published by
[Kaito Fukami](https://www.kaggle.com/code/kaitofukami/238-238-known-streams-v58-minimax-closed-loop).
The repository retains the executable Python artifact itself, not a downloaded
notebook archive.

The current integrity contract is:

- file size: **315,484 bytes**;
- SHA-256: `b041058ec187a8d0a01edc0eab8de068b53deca3e6c1973faf74ace6916ddcb9`;
- entry points: `agent`, `_kaggle_submission_entrypoint`, and
  `kaggle_agent_v58`;
- runtime dependencies: Python standard library only;
- policy set: ten routes, each containing 719 actions.

### Public Agent 2.1 Runtime architecture

Public Agent 2 dynamically reconstructs its packaged controller modules in memory and
exposes ten policy routes:

| Policy | Current role |
| --- | --- |
| `base_backbone` | Default route |
| `base_yarn` | First-shop YARN branch |
| `base_pet` | PET continuation selected from the second public shop |
| `recovery` | Public-state recovery branch |
| `smoothie` | FARMERS-to-SMOOTHIE continuation |
| `clone` | Persistent public-mirror continuation |
| `known_yarn` | Exact known-YARN public-state continuation |
| `ice_minimax` | ICE recovery/minimax continuation |
| `bakery_yarn` | BAKERY-to-YARN continuation |
| `pizza_recovery` | PIZZA-to-PET recovery continuation |

One controller is constructed on each early call. Its missed observation prefix
is replayed before it becomes available. After warm-up, all constructed
controllers are evaluated and the router returns the action from the selected
mode.

### Public Agent 2.2 Public-state routing

Routing depends only on visible configuration and observations:

| Tick | Public signal | Possible result |
| ---: | --- | --- |
| 72 | First shop, both public money values, WHEAT market inventory, and visible opponent assets | Recovery, ICE minimax, second-shop wait, or base route |
| 96 | Exact public signatures following a YARN opening | `known_yarn` continuation |
| 144 | Second unlocked shop | SMOOTHIE, BAKERY/YARN, or PIZZA/PET continuation |
| 360 | At least 240 consecutive ticks of exact public-farm equality | `clone` continuation |

The active router does not consult opponent identity, submission IDs, a hidden
seed, private opponent state, or future opponent actions.

### Public Agent 2.3 Current limitations

- All available controllers are evaluated after warm-up, including controllers
  that are not selected. This increases runtime cost and lets an unused
  controller failure affect the whole tick.
- A broad exception handler falls back to `_v51_safe_action` without exposing a
  diagnostic counter.
- Several route gates require exact money, inventory, and asset signatures. A
  small trajectory or engine divergence therefore keeps the agent on its base
  route rather than selecting a nearby recovery.
- Dynamic module registration in `sys.modules` is suitable for an isolated
  submission worker but may collide with other agents in a long-lived research
  process.
- The retained repository proves artifact integrity and import behavior; it
  does not contain the original evaluation notebook or an independently
  reproducible strategic benchmark for Public Agent 2.

## Public Agent 3 — Hardened V58 execution

**Original name:** Ye1  
**Source:** `src/agents/ye1.py`

`src/agents/ye1.py` keeps `src/agents/ye.py` as the unchanged public V58
reference and adds bounded execution, safety, and engine-parity improvements.
It preserves the V58 routes, signatures, thresholds, and public-state-only
routing contract.

Public Agent 3 warms the V58 route candidates through the hidden-shop opening, then selects
the `known_yarn` controller at the first public shop checkpoint. This controller
produced the highest paired final-money mean in the retained local screen and
is advanced alone for the rest of the episode.

Each required controller is isolated behind its own exception boundary. A
controller failure is counted in `_YE1_TELEMETRY` and falls back to that
controller's aligned route action instead of collapsing the whole tick to the
global PASS fallback. The telemetry records total calls, policy calls, policy
errors, outer errors, and fallback uses.

Disabled market-maker helpers are represented by a lazy no-op object, avoiding
their route copies and state allocation. Terminal liquidation uses the current
`episodeSteps`, `shedCapacity`, and `maxMarketOrdersPerTurn`, and projects
PICKUP, DROP, and PLACE before constructing the final SELL queue. Market value
calculations merge sparse `configuration.marketParams` overrides and effective
observation parameters, with observation values taking precedence.

The retained aggregate screen used seeds 11, 22, 33, and 44 in both seats
against Public Agent 2. Mean final money increased from 62,120.25 for the initial Public Agent 3 to
75,230.25 for the optimized variant; its paired Public Agent 2 opponents averaged 66,657.50.
Public Agent 3 won six of eight paired games, with no ties. Clean-process import,
fault-isolation, terminal PICKUP projection, sparse market parameters, and all
eight full-game completions passed. These are local results, not a leaderboard
claim. `src/agents/ye.py` remains the unchanged public V58 reference.

### Public Agent 2–3 verification and provenance

`src/agents/ye.py` remains the unchanged public V58 reference published by
[Kaito Fukami](https://www.kaggle.com/code/kaitofukami/238-238-known-streams-v58-minimax-closed-loop).

The repository retains the executable Python artifact itself. Structural checks
include clean-process import, the documented Public Agent 2 file size and SHA-256 digest,
its callable entry points, and the ten 719-action policy routes.

These checks establish artifact integrity and runtime structure. They do not
constitute a leaderboard claim or an independently reproducible strategic
benchmark for the original Public Agent 2 agent.

## Public Agent 4 — Readable public-route baseline

**Original name:** Jet  
**Source:** `src/agents/jet.py`

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

## Public Agent 5 — Safe fallback and final liquidation

**Original name:** Jet1  
**Source:** `src/agents/jet1.py`

`src/agents/jet1.py` keeps the same 719-step macro route and adds two small
runtime improvements.

### Public Agent 5.1 Staged runtime fallback

The baseline wraps the complete runtime pipeline in one broad exception
handler. Any unexpected error can therefore replace the entire intended tick
with `PASS`.

Public Agent 5 isolates the runtime stages:

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

### Public Agent 5.2 Observation-based final liquidation

The original route contains fixed final SELL quantities. Public Agent 5 replaces only
the last actionable market action with liquidation built from the observed
sellable inventory.

The logic:

1. derives the last actionable step from `episodeSteps`;
2. reads current shed contents;
3. projects same-tick `DROP` actions into the shed before market execution;
4. creates one SELL order for each non-empty sellable product;
5. respects the configured maximum number of market orders.

Earlier route actions remain unchanged.

## Public Agent 6 — Public-state market overlay

**Original name:** Jet2  
**Source:** `src/agents/jet2.py`

`src/agents/jet2.py` is a self-contained route agent. Its active macro route is
the same 719-step public V27 route embedded in Public Agent 5. The current implementation
keeps Public Agent 5's SELL ranking and adds one selected market intervention: bounded
preemption of an upcoming route sale when both public farms remain sufficiently
similar.

### Public Agent 6.1 Active runtime pipeline

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
Public Agent 5 SELL-slot ranking
        |
        v
final hand-count alignment
```

Each enhancement stage has its own exception boundary. If a stage fails, Public Agent 6
records the error in its per-seat runtime state and keeps the last valid action.
For the market stage, state changes are prepared on a copy and committed only
after the complete stage succeeds, so a failure cannot leave partially recorded
sale debt.

### Public Agent 6.2 Selected market behavior

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

### Public Agent 6.3 Code retained but inactive

The file still contains helpers for opponent-supply estimation, hysteretic
market experts, post-demand sale deferral, contiguous SELL-run ranking, and
sales on otherwise idle market ticks. These helpers are not called by the
active `agent` pipeline and must not be described as active Public Agent 6 strategy.

The active pipeline deliberately calls `_jet1_rank_sell_slots`; the alternative
run sorter and the general `_market_overlay` remain experimental utilities.

### Public Agent 6.4 Current limitations

- The agricultural plan is still a fixed route rather than a general planner.
- WEED recovery is local and does not prove that the complete route has been
  resynchronized after a larger divergence.
- Public-farm similarity is only a compact asset-distance heuristic. It does
  not establish that the opponent will sell the same product at the same time.
- Preemption optimizes timing against a route-like opponent and is not evidence
  of universal improvement against unrelated strategies.
- Several market helpers remain in the module despite being inactive, which
  increases review surface and makes the active pipeline less obvious.

## Public Agent 7 — Public Agent 3 backbone and terminal corrections

**Original name:** Jet3  
**Source:** `src/agents/jet3.py`

`src/agents/jet3.py` is the local baseline for the Public Agent 8 experiment. It keeps
the complete Public Agent 3 behavior and adds two bounded corrections without replacing
the selected route or its production strategy:

- `_jet3_final_drop` sends carried stock back to the nearest shed just in time
  for the existing terminal liquidation;
- `_jet3_filter_dead_seed_buys` removes seed purchases that the selected
  continuation will never plant;
- the existing observation-based terminal liquidation remains active at
  `episodeSteps - 2`.

On the existing eight-game holdout against Public Agent 3, Public Agent 7 averaged 85,286.25 final
money versus 84,041.75 for Public Agent 3, a gain of 1,244.50, and won all eight games.

## Public Agent 8 — Rejected late-hiring experiment

**Original name:** Jet4  
**Source:** `src/agents/jet4.py`

`src/agents/jet4.py` is a self-contained copy of Public Agent 7 with one additional
filter on `HIRE` market orders. The experiment was motivated by a separate
analysis of 813 top-10 replays: ranks 1–3 averaged about 105 late-game hires per
game, while ranks 8–10 averaged about 119. This correlation was treated only
as an experimental hypothesis: reduce late hiring that may not repay its cost
before the end.

Each `HIRE` order recruits one worker. The public `hires_today` count identifies
the next one-based Fibonacci cost, multiplied by `farmHandCostMult`. Public Agent 8
assumes a conservative return of one money unit per remaining worker-tick and
keeps a hire only when the ticks remaining through `episodeSteps - 2` are at
least its estimated payback time. Thus the filter is cost- and horizon-based;
it does not disable all hiring after a fixed day. All non-hiring behavior is
unchanged from Public Agent 7.

The direct benchmark used seeds 0–9, both seats for every seed, and the same
720-step configuration, for 20 paired games:

| Metric | Public Agent 7 | Public Agent 8 |
| --- | ---: | ---: |
| Mean final money | 81,960.70 | 80,391.10 |
| Minimum | 54,254.00 | 53,514.00 |
| Maximum | 116,539.00 | 114,292.00 |
| Wins | 20 | 0 |

The paired Public Agent 8 minus Public Agent 7 difference averaged -1,569.60, with a minimum of
-3,138.00 and a maximum of -463.00. Neither agent recorded an outer error,
policy error, or fallback. Public Agent 8 examined 5,580 hire orders, modified 120, and
therefore avoided 120 worker recruitments, or six per game.

Public Agent 8's record was 0 wins and 20 losses. The experiment is rejected because it
consistently degraded final money. The observed top-10 replay correlation does
not translate into a reproducible gain under this ROI-style payback rule, so
Public Agent 7 remains the stronger local baseline.

## Public Agent 9 — Dead fertilizer-purchase filter

**Original name:** Jet5  
**Source:** `src/agents/jet5.py`

`src/agents/jet5.py` starts directly from Public Agent 7 and does not inherit the
rejected Public Agent 8 experiment. Its only change tests whether Public Agent 7 buys fertilizer
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
inventory information leaves the Public Agent 7 action unchanged, and future fertilizer
collection is deliberately ignored to keep the filter conservative.

The final direct validation used seeds 0–99, both seats for every seed, and the
same 720-step configuration, for 200 paired games. Public Agent 7 averaged 84,209.90
final money and Public Agent 9 averaged 84,251.37. The paired Public Agent 9 minus Public Agent 7
difference was +41.46. Public Agent 9 recorded 184 wins and 16 losses, with positive
results on 94 of 100 seeds. Neither agent recorded an outer error, policy
error, or fallback.

The gain is small but reproducible across the larger validation. Public Agent 9 is the
current retained baseline.

## Public Agent 10 — Earlier monetization of finished products

**Original name:** Jet6  
**Source:** `src/agents/jet6.py`

### Initial Public Agent 10 experiment

Public Agent 10 started from Public Agent 9 with a late-Tomato viability filter. The hypothesis
came from a correlation in an earlier top-replay analysis, but the selected
Public Agent 9 continuation emitted no Tomato plant at all. Seeds 0–99, both seats,
therefore produced zero examined or modified Tomato actions, zero avoided
seeds, and a paired mean difference of 0.00. The experiment was inconclusive
and its code was removed.

### Terminal fertilizer correction

A runtime trace then exposed a real terminal defect. At steps 714–717 a worker
could attempt collection on an empty pasture, care for the adjacent animal,
and collect fertilizer only after it was too late to return it to the shed.
Public Agent 10 now starts that one-tile collection route at step 714, or advances a
step-715 `CARE` to `COLLECT_FERTILIZER`, only when collection, return, and drop
still fit before liquidation. Missing information and unrelated actions are
left unchanged.

The correction scored +1.00 on the 20-game screen. On seeds 0–99 it scored
84,225.79 mean final money versus 84,224.79 for Public Agent 9: paired mean +0.99,
paired range -21,913 to +21,914, 196 wins and 4 losses, with all 100 seeds
positive after combining their two seats. There were no errors or fallbacks.
Telemetry recorded 400 dead collections examined, 174 recovery routes
started, 373 collections advanced, and 373 fertilizer units recovered. The
rule is retained as a valid bug fix, not as the main Public Agent 10 improvement.

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
mostly implemented by Public Agent 9, endgame field filling was already present in the
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
fertilizer after Public Agent 9's filter, 7,246 sold wheat, 7,244 sold fertilizer,
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

On the seeds 0–9 screen, Public Agent 10 averaged 81,730.10 versus 80,564.40 for Public Agent 9.
The paired gain was +1,165.70 (+1.45%), with 18 wins, 2 losses, 9 positive
seeds, 1 negative seed, and no errors. The full seeds 0–99 validation was:

| Metric | Public Agent 9 | Public Agent 10 |
| --- | ---: | ---: |
| Mean final money | 83,019.35 | 83,979.63 |
| Median | 82,499.00 | 83,438.00 |
| Minimum | 41,061.00 | 41,934.00 |
| Maximum | 138,151.00 | 138,732.00 |

The paired mean gain was +960.27, or +1.16%, with a paired range of -21,250
to +23,233. Public Agent 10 recorded 190 wins, 10 losses, and no draws. At seed level,
96 were positive, 4 negative, and none neutral. The large paired extremes were
opposite-seat interaction effects; their seed totals remained representative,
and the gain was not dependent on a few outliers. There were no outer errors,
policy errors, or fallbacks. Early-sale telemetry recorded 7,028 opportunities,
6,469 added orders, 42,101 offered units, and 3,001 opportunities observed on
turns whose market order list was already full.

The untouched holdout used seeds 100–129, both seats. Public Agent 9 averaged 80,703.08
and Public Agent 10 averaged 81,842.42. The paired gain was +1,139.33, or +1.41%, with
a range of -219 to +3,009. Public Agent 10 recorded 59 wins, 1 loss, and no draws; all
30 seeds were positive. There were no errors or fallbacks. Holdout telemetry
recorded 2,104 opportunities, 1,936 added orders, 12,723 offered units, and
900 full-market skips. No threshold was tuned on the holdout.

The early-sale mechanism is therefore retained. Together with the terminal
fertilizer bug fix, it makes Public Agent 10 the **final retained local baseline** at project
closure. This conclusion is limited to the paired local benchmarks and is not a leaderboard
claim.

## Shared benchmark protocol

Every Public Agent 4 modification should be compared directly with the previous Public Agent 4
version.

Recommended comparison:

```text
same environment configuration
same seeds
both player seats when relevant
Public Agent 4 vs Public Agent 5
```

Record at minimum:

- final money/reward;
- minimum, maximum and mean over repeated games;
- completion/errors;
- final shed inventory;
- final carried inventory;
- number of invalid or lost route actions if instrumented.

A change should remain isolated until its effect is understood.

## Archived improvement candidates

The project is closed. The following candidates were not implemented and are retained only as
research notes; any later reuse should preserve the macro route first.

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
measured, because the fixed route is currently the main source of Public Agent 4's
strength.

## Documentation and provenance

Keep the public-route origin explicit in the repository and preserve any
required attribution or license notices from the original public source.

Public Agent 4 should not be presented as an original CHI strategy. The project's
contribution in this branch is the readable reconstruction, benchmarking and
subsequent runtime/strategy improvements.
