# Heuristic Ideas v1 — Corrected Daily Planner

[Previous version: none](#) · [Next version →](./heuristic_ideas_v2.md)

> **Series convention**
>
> - `v1` is the complete baseline of the heuristic-ideas series.
> - `v2`, `v3`, and `v4` are **strict deltas over the immediately preceding version**.
> - A delta inherits its direct predecessor in full unless it explicitly adds, replaces, or corrects a rule.
> - Inheritance is transitive: later versions do not use older versions as parallel design parents.
> - [`heuristic_ideas_final.md`](./heuristic_ideas_final.md) is the complete standalone snapshot after the whole chain and has no associated agent.

## Identity

| Field | Value |
| --- | --- |
| Version | `v1` |
| Original source | `detail_corrige` |
| Associated agent | `chi12.py` |
| Role | Complete baseline of the heuristic planner |
| Improved by | [`v2`](./heuristic_ideas_v2.md) |

## Main idea

Build each day from the current game state, turn needs into prioritized tasks, group related actions, add the required logistics, assign routes and workers, then execute while locally repairing the plan when the observed state changes.

## Core ideas

### 1. Plan every day from the real state

At the start of each day, read the current state and rebuild the useful work from what actually exists: plants, animals, weeds, stock, workers, shed capacity, market needs, and possible production.

The daily pipeline is conceptually:

`economy -> tasks -> placement -> priorities -> bundles -> logistics -> routes -> capacity/HIRE -> execution/replanning`

### 2. Survival work comes before optimization

Mandatory maintenance must not be sacrificed for optional profit:

- water plants when another missed day would create a survival problem;
- feed animals when another missed day would make them escape;
- harvest before output is lost or an animal reaches storage saturation;
- protect mandatory planting-day watering.

These actions are treated as `CRITICAL`.

### 3. Separate survival, production, yield, preparation, and secondary work

Tasks are not all equivalent. The planner distinguishes:

- `CRITICAL`: prevents loss or failure;
- `PRODUCTION`: required harvest, planting, building, placement, or productive feeding;
- `YIELD`: fertilizing, care, and useful bonus watering;
- `PREPARATION`: digging or installation needed for future production;
- `SECONDARY`: non-urgent fertilizer collection or weed removal.

Deadlines and economic value refine the ordering inside these categories.

### 4. Place production to reduce future maintenance cost

Placement is not based only on finding a free tile. Candidate tiles are scored using:

- distance to the shed;
- future maintenance visits;
- proximity to similar production;
- route obstruction;
- space usage.

High-maintenance production should stay closer to efficient routes and shed access. Animals are therefore more sensitive to placement than simple temporary crops.

### 5. Keep dependent actions together

Actions concerning the same tile should form a bundle whenever possible.

Typical bundles include:

- `DIG -> PLANT -> WATER`;
- `BUILD -> PLACE -> FEED -> CARE` for a new animal;
- `HARVEST -> optional DIG -> PLANT -> optional FERTILIZE -> WATER` when replanting.

The planner must preserve ordering constraints, especially `FERTILIZE before WATER` and `WATER before HARVEST` when relevant.

### 6. Treat logistics as part of the plan

A route is only feasible if the worker has the resources needed to execute it.

The planner therefore:

- reserves seeds, fertilizer, animals, and feed;
- creates purchase dependencies when stock is missing;
- computes exact pickup quantities;
- loads route resources before the worker leaves the shed area;
- tracks future worker inventory after harvests;
- schedules returns and `DROP` actions when needed.

### 7. Protect shed capacity before a required DROP

Storage pressure must be solved before it blocks required production.

If a planned `DROP` would overflow the shed, the planner should free capacity in advance by selling stock, inserting an earlier drop, or redistributing routes.

A required harvest should not be postponed only to avoid shed pressure.

### 8. Build routes around urgency and locality

Routes start from the most urgent task bundles and add nearby compatible work while preserving deadlines.

Insertion balances:

- travel distance;
- action cost;
- deadline risk;
- same-area opportunities;
- same-type opportunities.

The goal is not globally optimal routing, but practical routes that complete important work on time.

### 9. HIRE exists to make planned work feasible

Capacity planning determines whether existing workers can execute all important routes. If not, the planner can schedule `HIRE` actions and assign the new workers after their availability tick.

A route is finalized only after checking:

- worker spawn and availability;
- pickups;
- travel and action time;
- return to shed;
- deadlines;
- market dependencies;
- shed capacity.

### 10. Replan locally when reality differs from the plan

Execution continuously checks whether assumptions remain true.

Important changes include:

- new shops or meaningful price changes;
- opponent actions;
- unexpected weeds;
- different harvest/production results;
- failed `BUY` or `HIRE`;
- workers falling behind schedule;
- inventory or shed saturation.

When something changes, keep completed work, paid hires, and valid routes whenever possible, and rebuild only the affected future work.

### 11. Respect the market order limit

`SELL`, `BUY`, and `HIRE` actions share the market limit of 10 orders per tick.

Identical orders can be merged when legal. If the limit is exceeded, dependency-critical and deadline-critical orders must be preserved before lower-priority economic orders.

### 12. End-of-game liquidation is explicit

The final day is not treated like a normal day.

With `episodeSteps = 720`, liquidation and the final `DROP` must be completed no later than day 29, hour 22. The planner should finish with no important harvest forgotten and no worker inventory stranded away from the shed.

## Key invariants

- Never leave a newly planted crop without its mandatory watering.
- Never let survival `WATER` or `FEED` lose to optional work.
- Never schedule a route without the resources needed to complete it.
- Never let a required `DROP` exceed shed capacity.
- Never postpone a required harvest only because storage planning is poor.
- Never execute more than 10 market orders in one tick.
- Preserve already completed or still-valid work during replanning.
- Complete final liquidation by the last playable final-day tick.

## What v1 establishes

`v1` is the full reference planner. Its only direct successor is [`v2`](./heuristic_ideas_v2.md). All later behavior is inherited transitively through the version chain rather than treating `v1` as a parallel parent.


---

## Navigation

Previous version: none · [Next version →](./heuristic_ideas_v2.md)
