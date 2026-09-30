# Heuristic Ideas v3 — Unified Optimized Planner

[← Previous version](./heuristic_ideas_v2.md) · [Next version →](./heuristic_ideas_v4.md)

> **Series convention**
>
> `v3` is a **strict delta over `v2`**. It inherits `v2` in full; because `v2` already
> inherits `v1`, all `v1` behavior remains available transitively without making `v1`
> a second direct parent.

## Identity

| Field | Value |
| --- | --- |
| Version | `v3` |
| Original source | `detail_opti` |
| Associated agent | `chi14.py` |
| Role | Strict delta over [`v2`](./heuristic_ideas_v2.md) |
| Improves | [`v2`](./heuristic_ideas_v2.md) |
| Improved by | [`v4`](./heuristic_ideas_v4.md) |

## Main idea

Stop letting economy, routing, market handling, capacity, and execution rely on separate approximations. Make every subsystem consume one shared forecast, one reservation model, one task representation, and one validated market calendar so that a decision accepted by one part of the planner is also feasible for the others.

`v3` inherits [`v2`](./heuristic_ideas_v2.md) in full. Because `v2` already inherits `v1`, every unchanged `v1` rule remains available transitively; `v3` has only one direct predecessor.

## Core ideas added in v3

### 1. One shared forecast for all planner decisions

Maintain a single derived-state forecast from the current absolute tick to the end of the game.

The forecast projects only the affected parts after a change and tracks:

- plant and animal state;
- watering, feeding, and care;
- survival;
- yields and production dates;
- fertilization;
- decay and saturation;
- maintenance requirements;
- resources and harvestable output;
- tile occupation and future release.

Production, placement, land, routing, market, and endgame logic all read from this same forecast.

### 2. Economy, placement, and expansion become one coherent plan

Economic strategy should produce dated commitments rather than isolated wishes.

It evaluates only production that can still create positive value before game end and includes the complete chain:

`production -> maintenance -> resources -> harvest -> return -> DROP -> SELL`

It also includes cash, hires, stock, and market slots.

`DECIDE_LAND_PURCHASE()` still exists from `v2`, but now consumes this common plan instead of maintaining a separate economic approximation.

### 3. Generate dependency-aware `TaskGroup` objects directly

Replace the multi-stage transformation from raw tasks to bundles and logistics with direct generation of stable groups.

A `TaskGroup` carries:

- position;
- ordered actions;
- priority;
- deadline;
- required resources;
- estimated value;
- dependencies;
- optional worker assignment.

Prerequisites inherit the urgency of what depends on them.

Stable IDs prevent duplicated tasks when generation is called repeatedly without a meaningful state change.

### 4. Merge routing, capacity, logistics, and `HIRE`

Worker assignment should evaluate the real cost of inserting a group into a route.

Insertion cost includes:

- travel;
- action time;
- pickups;
- waiting for resources;
- return and `DROP`;
- deadlines;
- stock effects;
- market effects.

If an important group still cannot be assigned, test a new worker and include the Fibonacci hire cost, spawn, availability tick, remaining route capacity, travel, return, and deadline.

A `HIRE` is accepted only when it actually makes the target work feasible.

### 5. Prefer small local route improvements over a complex global solver

After obtaining feasible routes, try limited moves or swaps between task groups.

Accept a change only if it strictly improves route cost without breaking deadlines or reservations.

If a group combines an urgent harvest with an optional replacement, remove the optional replacement first and retry the harvest alone.

The goal is a better heuristic planner, not a general-purpose VRP system.

### 6. Use one stock and market calendar

All `BUY`, `SELL`, `HIRE`, and related market intentions must be scheduled through one validated calendar.

The calendar:

- orders actions by dependency;
- ensures financing sales happen before the purchases or hires they fund;
- respects the 10-orders-per-tick limit;
- simulates cash, stock, reservations, and prices;
- reports conflicts back to dependent tasks.

The 11th order must never be silently discarded.

A delayed purchase invalidates dependent pickups or planting. A delayed hire invalidates route capacity based on the old availability tick.

### 7. Replan by repairing only the affected future

Do not broadly rebuild the planner after every observation change.

First ask whether the change affects feasibility, the sign of expected gain, or the chosen economic action. If not, keep the current plan.

When repair is needed:

- identify the local cause;
- preserve confirmed facts and committed route prefixes;
- preserve paid workers and still-valid routes;
- release only invalid future reservations and affected route suffixes;
- regenerate only affected task groups;
- reassign only new or displaced groups.

A local issue can still propagate to several routes when they share the same resource or market dependency.

### 8. Integrate endgame constraints into every decision

Endgame logic should not be a final cleanup pass.

Reject new production, animals, or expansion whenever the full cash-out chain cannot repay the decision before game end:

`installation + production + harvest + return + DROP + SELL`

Also remove maintenance or spending with no remaining cashable effect, such as useless late fertilizer, care, purchases, or optional hires.

Plan the last harvest, return, drop, and sale backward from the final liquidation deadline.

### 9. Turn known edge cases into explicit verification cases

The planner should be tested against concrete invariants, including:

- exact feed pickup after subtracting inventory already carried;
- seed reservation preventing concurrent over-planting;
- hired worker availability beginning one tick after `HIRE`;
- freeing shed capacity before, not at, an overflowing `DROP`;
- repairing market conflicts beyond 10 orders rather than truncating them;
- rejecting land when no additional profitable production exists;
- rejecting land whose future maintenance is infeasible.

## Key invariants

- Every subsystem uses the same forecast and reservations.
- Repeated generation without state change must not duplicate planned work.
- Logistics is part of route feasibility, not patched afterward.
- A hire is useful only if it makes otherwise infeasible important work feasible.
- Market dependencies are scheduled explicitly and never silently truncated.
- Delayed market actions invalidate dependent future actions.
- Replanning preserves valid committed work and repairs only affected suffixes.
- Every new economic decision must still complete its full cash-out chain before game end.

## What v3 changes relative to v2

`v3` does not mainly add new game rules. It reorganizes the planner so existing rules are evaluated consistently. Its central improvement is coherence: one forecast, dependency-aware task groups, integrated assignment and hiring, one market calendar, local repair, and endgame-aware feasibility everywhere.


---

## Navigation

[← Previous version](./heuristic_ideas_v2.md) · [Next version →](./heuristic_ideas_v4.md)
