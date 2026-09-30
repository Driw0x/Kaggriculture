# Heuristic Agents

This document complements [chi_agents.md](./chi_agents.md).

`chi_agents.md` describes the historical CHI lineage from the initial fixed opening to
CHI10. This document isolates the later **heuristic-planner branch** built again from
CHI3's production model and documented through one strict sequence of heuristic ideas:

```text
IMPLEMENTED AGENT LINEAGE

CHI3
  |
  v
heuristic_ideas_v1 -> CHI12
  |
  v
heuristic_ideas_v2 -> CHI13
  |
  v
heuristic_ideas_v3 -> CHI14

DESIGN-ONLY CONTINUATION

heuristic_ideas_v3
  |
  v
heuristic_ideas_v4
  |
  v
heuristic_ideas_final
```

Design documents:
[ideas_v1](./ideas/heuristic_ideas_v1.md) →
[ideas_v2](./ideas/heuristic_ideas_v2.md) →
[ideas_v3](./ideas/heuristic_ideas_v3.md) →
[ideas_v4](./ideas/heuristic_ideas_v4.md) →
[ideas_final](./ideas/heuristic_ideas_final.md)

The design chain is strict: `v1` is the baseline, each of `v2`, `v3`, and `v4` improves
only its immediate predecessor, and `final` is the complete standalone strategy after the
whole lineage has been resolved. The implemented agent lineage stops at `CHI14`. The project
is now closed: `v4` and `final` remain design-only, and later implementation attempts,
including `CHI16` / `chi_final`, did not produce a validated successor and are not retained
as source agents.

The lineage above is a **design lineage**. Code reuse can remain more direct where that is
useful: design inheritance and Python import structure do not need to be identical.

---

## 1. Objective

The purpose of this branch is different from the incremental CHI1–CHI10 history.

The branch starts from CHI3 because CHI3 already provides the reusable production
description needed by a general planner:

- crop and animal state descriptions;
- harvest schedules;
- coordinate/path helpers;
- multi-day production semantics.

The objective is then to replace fixed or locally greedy behavior with an increasingly
explicit planning pipeline:

```text
observation
    |
    v
production state / forecast
    |
    v
economic choices
    |
    v
placements and land decisions
    |
    v
task groups with priorities and deadlines
    |
    v
routing + capacity + HIRE
    |
    v
market orders and storage constraints
    |
    v
execution
    |
    v
local replanning from observations
```

The four versioned idea documents progressively make this pipeline more concrete, and the
final document resolves them into one complete standalone strategy. In the closed project
snapshot, the implemented agent lineage stops at `CHI14`; `v4` and `final` remain design-only
stages.

---

## 2. Source mapping

| Agent | Design source | Main role |
| --- | --- | --- |
| `chi3.py` | CHI historical branch | Production/state base |
| `chi12.py` | [ideas_v1](./ideas/heuristic_ideas_v1.md) | Correct daily planner and execution model |
| `chi13.py` | [ideas_v2](./ideas/heuristic_ideas_v2.md) | Planned land expansion over CHI12 |
| `chi14.py` | [ideas_v3](./ideas/heuristic_ideas_v3.md) | Unified forecast, routing, market calendar and endgame-aware planning |

Design stages without an associated agent:

| Design | Status | Main role |
| --- | --- | --- |
| [ideas_v4](./ideas/heuristic_ideas_v4.md) | Design only | Market-aware tactical and marginal economic layer over `v3` |
| [ideas_final](./ideas/heuristic_ideas_final.md) | Design only | Complete consolidated strategy and implementation contract |

---

## 3. Base — CHI3 production model

CHI3 is the common starting point of the heuristic branch.

CHI12 explicitly imports from CHI3:

```python
ANIMAL_STATE
CROP_PRODUCTION
CROP_STATE
coordinates_to_path
distance
```

The CHI12 validation also verifies that CHI3 remains read-only during the rewrite.

The branch therefore keeps CHI3's production vocabulary while replacing the planning
and execution around it.

### Retained concepts

The retained base includes:

- the five crop families used by the planner;
- Goose, Cow and Sheep production;
- crop harvest timing;
- animal production timing;
- reusable Manhattan path construction;
- observable crop/animal state.

### What the branch changes

The new branch does not simply continue CHI3's route allocator.

It progressively introduces:

- explicit task priorities;
- action deadlines;
- resource-aware route compilation;
- scheduled PICKUP and DROP;
- market availability at T+1;
- storage protection;
- global worker assignment;
- land-expansion evaluation;
- dated production lots;
- dynamic market-price projection;
- full executable economic rollout.

---

# 4. CHI12 — [ideas_v1](./ideas/heuristic_ideas_v1.md)

`src/agents/chi12.py` is associated with the baseline planner described by
[ideas_v1](./ideas/heuristic_ideas_v1.md).

The source file states the relationship directly:

```text
CHI12: CHI3 production with the daily planner described by `heuristic_ideas_v1`.
```

CHI3 is treated as a read-only production reference.

## 4.1 Planner structure

[ideas_v1](./ideas/heuristic_ideas_v1.md) organizes each day around the following sequence:

```text
read current state
    -> economic strategy
    -> generate daily tasks
    -> choose placements
    -> prioritize tasks
    -> build task groups
    -> add logistics
    -> build candidate routes
    -> calculate capacity / HIRE
    -> finalize routes
    -> execute and replan
```

This becomes the first explicit daily planner of this branch.

## 4.2 Task generation

CHI12 converts the observed farm into ordered tile-local task bundles.

Examples include:

```text
crop:
    FERTILIZE
    WATER
    HARVEST
    DIG
    PLANT
    WATER

animal:
    HARVEST
    COLLECT_FERTILIZER
    FEED
    CARE
```

Every task carries:

- a priority;
- a deadline;
- a tile position;
- an estimated value;
- the ordered actions that must be executed on that tile.

The implemented priority classes are:

```text
CRITIQUE
PRODUCTION
RENDEMENT
PREPARATION
SECONDAIRE
```

This keeps survival and deadline-sensitive work ahead of optional yield or cleanup work.

## 4.3 Placement

`choose_placements` retains already existing production and reconstructs the CHI3
portfolio on available tiles.

Placement cost considers:

- expected number of visits;
- distance to the nearest shed access;
- proximity to similar production;
- structure compatibility.

At this stage the planner does not speculate on expansion: the CHI3 portfolio fits in
the initial NW quadrant.

## 4.4 Explicit logistics

The `v1` design makes inventory movement part of the plan rather than an
afterthought.

CHI12 computes:

- required Wheat for FEED;
- required Fertilizer for FERTILIZE;
- animals to PICKUP before PLACE;
- seeds required by planned PLANT actions;
- availability of purchases at T+1;
- return paths to the shed;
- final DROP actions.

`compile_route` rejects a route when an action or the final return misses the playable
deadline.

## 4.5 Storage protection

`protect_storage` chronologically simulates:

```text
PICKUP
DROP
SELL
BUY_PRODUCT
BUY_ANIMAL
```

before accepting the route.

A return may be delayed if the shed cannot accept its cargo, but the planner does not
delay a harvest merely to keep output outside the shed.

## 4.6 HIRE and routing

The first implementation uses greedy route insertion.

For each worker the planner:

1. selects a candidate task;
2. recompiles the complete route;
3. verifies deadlines;
4. verifies logistics;
5. verifies storage;
6. accepts the insertion only when the complete route remains executable.

If the existing workforce cannot cover required work, the planner evaluates additional
farm hands with the Fibonacci HIRE cost and the T+1 worker availability rule.

## 4.7 Observation-checked execution

Execution is persistent across the day.

A local replan can be triggered by:

- an unexpected worker position;
- a refused purchase;
- a missing hired worker;
- an unexpected weed;
- a changed production tile;
- a yield mismatch;
- a newly opened shop;
- a sufficiently large price change.

Valid routes are retained whenever possible instead of rebuilding the whole plan.

---

## 5. CHI12 validation

A dedicated Codex validation report is available for CHI12.

### Engine behavior verified

The validation confirms several engine constraints used by the planner:

- worker actions execute before market orders;
- purchases and HIRE issued at T become usable at T+1;
- a same-tick DROP can be sold;
- a same-tick sale does not free shed space before that DROP;
- with the default 720-step game, the last actionable step is 718;
- the final explicit return and liquidation must therefore fit before the end.

### Tests

The CHI12-specific suite contains **28 tests**.

The full test suite at the time of the validation contains **68 passing tests**.

The cases cover, among other things:

- PLANT followed by mandatory WATER;
- animal FEED resource requirements;
- multiple FERTILIZE actions;
- placement of all three animal species;
- FERTILIZE/WATER/HARVEST ordering;
- Tomato and Strawberry replacement;
- return and DROP cost;
- weeds;
- HIRE and BUY availability at T+1;
- the market-order limit;
- full-shed and simultaneous-return cases;
- final liquidation;
- route preservation during replanning;
- rejected purchases/HIRE;
- unexpected production changes.

### CHI3 comparison

The retained benchmark uses seeds 0–19 in both seats, for 40 games per agent.

| Agent | Games | Minimum | Maximum | Mean | Median | Invalid |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CHI3 | 40 | 0 | 0 | 0 | 0 | 0 |
| CHI12 | 40 | 55,033 | 62,953 | 59,597.25 | 60,306 | 0 |

This comparison has an important limitation: CHI3 does not emit SELL orders in the
tested code. The result therefore validates CHI12's complete playable/economic loop,
but it does **not** isolate the value of the new routing algorithm alone.

---

# 6. CHI13 — [ideas_v2](./ideas/heuristic_ideas_v2.md)

`src/agents/chi13.py` is the targeted evolution of CHI12 associated with the strict
`v2` delta in [ideas_v2](./ideas/heuristic_ideas_v2.md).

Its source summarizes the goal as:

```text
CHI13: targeted CHI12 evolution with global routing and planned land use.
```

The implementation reuses CHI12's tested engine-facing primitives.

## 6.1 Main design change

[ideas_v2](./ideas/heuristic_ideas_v2.md) adds a missing top-level economic decision before the normal daily
task pipeline:

```text
DECIDER_ACHAT_TERRAIN()
```

Land is no longer purchased simply because the farm is full.

Expansion must correspond to a real additional production need that cannot be placed
on already unlocked land in time.

## 6.2 Land-order model

The implementation follows the legal expansion order:

```text
NW -> NE -> SW -> SE
```

with costs:

```text
1000
2000
4000
```

The planner does not invent a choice between arbitrary quadrants. It decides whether
to buy the next legal quadrant and how to exploit it.

## 6.3 Concrete expansion plan

Before a BUY_LAND is accepted, CHI13 estimates:

- remaining profitable production;
- tile positions in the new quadrant;
- seed cost;
- additional HIRE cost;
- current committed market cost;
- route capacity;
- whether the installation still fits before the end.

A candidate expansion must therefore be both:

```text
affordable
and
routable
and
profitable
```

The layout for the new quadrant is reserved only after the land purchase is confirmed.

## 6.4 Global worker assignment

CHI12 builds routes largely worker by worker.

CHI13 changes the allocator so a task is first tested across all existing workers.
The selected insertion minimizes the incremental route cost among feasible workers.

The intended order becomes:

```text
existing workers first
    -> fit as many required groups as possible
    -> only then consider HIRE
```

This directly implements the [ideas_v2](./ideas/heuristic_ideas_v2.md) goal of avoiding a hire when another
existing worker can absorb the work.

## 6.5 Centralized market scheduling

CHI13 adds one final consolidation step for market orders.

Orders are:

- merged;
- deduplicated;
- limited to the configured number of market orders per tick;
- carried to later ticks when required.

This gives one owner to the market-slot constraint instead of letting independent
planner blocks compete for the same slots.

## 6.6 Execution relationship

CHI13 keeps the CHI12 execution model:

- persistent routes;
- confirmation from observations;
- failed BUY/HIRE detection;
- selective route invalidation;
- local replanning;
- storage protection.

The main change is therefore not a new action executor, but a stronger planner placed
above the tested CHI12 primitives.

---

# 7. CHI14 — [ideas_v3](./ideas/heuristic_ideas_v3.md)

`src/agents/chi14.py` is associated with the strict `v3` delta in
[ideas_v3](./ideas/heuristic_ideas_v3.md).

Its source describes the version as:

```text
CHI14: CHI13 routing with dated marginal crop economics.
```

CHI14 therefore preserves the CHI13 routing/execution layer and focuses on the
economic value of production and expansion.

## 7.1 Single forecast-oriented architecture

[ideas_v3](./ideas/heuristic_ideas_v3.md) simplifies the earlier long planner into six tightly connected blocks:

```text
forecast
    -> economy / placement / expansion
    -> task groups and dependencies
    -> routing / capacity / HIRE
    -> stock and market calendar
    -> execution / local replanning / endgame
```

The objective is to use the same dated state throughout the planner instead of letting
routing, economics and market code maintain independent approximations.

## 7.2 Exact market-price projection

CHI14 uses the Kaggriculture engine pricing function for projected transactions.

`project_market` simulates:

- unit-by-unit SELL pricing;
- BUY_PRODUCT pricing;
- current market inventory;
- already opened shop consumption;
- town-center consumption;
- transaction order by tick.

The planner first verifies that the local pricing function reproduces the current
observed quote before trusting the projection.

## 7.3 Dated production lots

Instead of valuing a crop as a single static amount, CHI14 creates dated sellable lots.

For each production it tracks enough information to estimate:

```text
harvest day
    -> earliest feasible return
    -> DROP
    -> SELL tick
```

Existing plants and planned plants are treated separately so a production is not
double-counted.

Output that cannot be sold before the end contributes no projected revenue.

## 7.4 Marginal contribution

The central decision becomes a comparison between two complete portfolios:

```text
reference layout
versus
reference layout + one candidate production
```

For the candidate, CHI14 recomputes:

- projected revenue;
- seed cost;
- HIRE cost;
- route feasibility;
- land cost when applicable.

The resulting quantity is a marginal contribution rather than a fixed crop score.

## 7.5 Prudent scenario

CHI14 evaluates both:

- a central projection;
- a more conservative projection including visible opponent crop supply.

The planner can therefore use:

```text
contribution_prudent
```

when deciding whether a candidate remains worthwhile.

This still uses only visible opponent production; it does not invent hidden opponent
inventory.

## 7.6 Marginal land expansion

Land evaluation now grows the proposed new layout incrementally.

For each candidate tile:

1. test each crop;
2. compute marginal contribution;
3. rebuild the CHI13 route plan;
4. verify that the tile is actually assigned;
5. recompute the contribution with the new route;
6. keep the addition only if the prudent contribution remains positive.

The full land cost is then charged once to the candidate expansion prefix.


---

# 8. Design v4 — [ideas_v4](./ideas/heuristic_ideas_v4.md)

`v4` has **no associated agent**. It is the strict design delta that follows the design
implemented by CHI14 / `v3`.

`v4` does not redefine the planner from scratch. It inherits the complete `v3` design and
adds a market-aware tactical layer on top of the unified forecast, routing, market calendar,
local repair, and endgame model.

## 8.1 Main design change

The central new chain is:

```text
shop demand
    -> own + opponent supply
    -> future market inventory
    -> future price
    -> marginal value
    -> production / hold / sell decisions
```

The design therefore evaluates not only whether work is feasible, but whether the next unit,
tile, worker, land purchase, or sale still improves expected value.

## 8.2 Labor and spatial constraints

The `v4` design adds:

- the strategic worker ceiling `MAX_WORKERS = 14`;
- marginal-value testing before another HIRE;
- center-near animal placement;
- a central `2 x 2` reservation against long-duration crops;
- land-time-aware economic comparison.

These rules sit above the routing and feasibility machinery inherited from `v3`.

## 8.3 Market and opponent-aware economics

`v4` adds explicit reasoning about:

- visible opponent production and timing;
- future market inventory and price;
- marginal production value;
- sell-versus-hold value;
- sale price impact;
- cash urgency;
- product-level inventory behavior.

Historical formulas and fixed schedules in `v4` remain experimental unless the final
consolidated design explicitly promotes them.

## 8.4 Tactical land policy

`v4` adds preferred land timing branches and an explicit operating cash floor while keeping
the inherited feasibility and profitability gates.

The exact active interpretation of those tactical rules is resolved in
[ideas_final](./ideas/heuristic_ideas_final.md).

---

# 9. Final consolidated design — [ideas_final](./ideas/heuristic_ideas_final.md)

`final` also has **no associated agent**. It is a documentation/design snapshot, not an
implemented CHI version. The project closed without a validated `CHI16` / `chi_final`
successor.

Unlike `v2`, `v3`, and `v4`, the final document is **not a delta**. It is the standalone
snapshot obtained after the full design chain has been applied and contradictions have been
resolved.

## 9.1 Canonical final design

The final strategy defines, in one place:

- verified mechanical constraints;
- one shared physical/economic forecast;
- separation of farm-side supply from global market inventory;
- `LOW / BASE / HIGH` opponent scenarios;
- conditional asset preservation and abandonment;
- dependency-aware `TaskGroup` planning;
- exact resource, tile-time, cash, storage, worker-time, and market-slot reservations;
- `MAX_WORKERS = 14`;
- active placement geometry and fixed opening rules;
- active scheduled land expansion plus economic unscheduled expansion;
- marginal production and exact sale-quantity search;
- local repair instead of broad replanning;
- backward endgame cash-out planning;
- a verification and implementation contract.

## 9.2 Historical ideas remain traceable

Ideas that were considered but are not active are retained inside the final document as
benchmark-only history. The versioned files remain useful to understand how each change
entered the design lineage, while `final` is the complete resolved snapshot for any future
implementation.

---

# 10. Evolution of the heuristic branch

The progression is a strict design chain: each version answers one additional planner
question without using older versions as parallel parents.

## CHI12 / v1 — Can the work actually be executed?

[ideas_v1](./ideas/heuristic_ideas_v1.md) establishes the complete daily baseline:

```text
What must be done?
When must it be done?
What resources must be carried?
Can a worker complete the route and return?
Can the shed accept the result?
```

## CHI13 / v2 — Should the farm expand?

[ideas_v2](./ideas/heuristic_ideas_v2.md) changes only the land decision inherited from `v1`:

```text
Is additional profitable production blocked by land?
What is the best no-purchase plan?
Can the new quadrant be exploited in time?
Does the complete expansion plan repay its cost?
```

## CHI14 / v3 — Can every subsystem reason from the same plan?

[ideas_v3](./ideas/heuristic_ideas_v3.md) reorganizes the inherited planner around:

```text
one forecast
-> stable TaskGroups
-> integrated routing / logistics / HIRE
-> one market calendar
-> local repair
-> endgame-aware feasibility
```

## v4 — How should feasible work react to the market and opponent?

[ideas_v4](./ideas/heuristic_ideas_v4.md) adds:

```text
shop demand
-> own/opponent supply
-> future market inventory
-> expected price
-> marginal production / labor / sell value
```

## final — What is the complete resolved strategy?

[ideas_final](./ideas/heuristic_ideas_final.md) applies the whole chain, resolves conflicting
historical heuristics, separates active rules from benchmark-only ideas, and remains the
archived standalone design reference. No validated implementation of this stage was retained
before project closure.

---

# 11. Architecture summary

| Version | Planning | Routing / labor | Economy | Expansion |
| --- | --- | --- | --- | --- |
| CHI3 | Dynamic production maintenance | Dynamic daily routing | Minimal | None |
| CHI12 / v1 | Priorities + deadlines + resource bundles | Executable routes + HIRE | Baseline economic decisions | No implicit speculative expansion |
| CHI13 / v2 | v1 + explicit land decision | Inherited planner, validated against expansion | No-land vs land-plan comparison | Reserved, observed, economically validated expansion |
| CHI14 / v3 | Shared forecast + stable `TaskGroup` | Integrated assignment, logistics and HIRE | One validated market calendar | Expansion consumes the shared plan |
| v4 (design only) | v3 + tactical market layer | Worker cap + marginal labor value | Opponent/price/marginal sell-and-production logic | Tactical timing priors + cash floor |
| final (design only) | Complete resolved strategy | Exact reservations + local repair | Final-cash objective + exact marginal search | Active schedule + economic unscheduled gate |

---

# 12. Relationship with `chi_agents.md`

The two documents intentionally describe different histories.

`chi_agents.md` remains the record of the original CHI progression:

```text
chi.py -> CHI1 -> ... -> CHI10
```

This document records the separate heuristic-planner design lineage:

```text
CHI3
  -> heuristic_ideas_v1    -> CHI12
  -> heuristic_ideas_v2    -> CHI13
  -> heuristic_ideas_v3    -> CHI14
  -> heuristic_ideas_v4    -> design only
  -> heuristic_ideas_final -> design only
```

Canonical design chain:

[ideas_v1](./ideas/heuristic_ideas_v1.md) →
[ideas_v2](./ideas/heuristic_ideas_v2.md) →
[ideas_v3](./ideas/heuristic_ideas_v3.md) →
[ideas_v4](./ideas/heuristic_ideas_v4.md) →
[ideas_final](./ideas/heuristic_ideas_final.md)

CHI3 therefore appears in both documents for different reasons:

- in `chi_agents.md`, it is the third historical CHI iteration;
- in `heuristic_agents.md`, it is the reusable production/state foundation from which
  the later heuristic planner was rebuilt.


That separation keeps the repository history readable without presenting CHI12 onward as
direct chronological successors of CHI10.
